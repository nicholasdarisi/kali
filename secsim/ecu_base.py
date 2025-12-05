# ecu_base.py

import can
import time
import threading
import random
from enum import Enum, auto

# --- Definizione Stati e Ruoli ---

class NodeState(Enum):
    ERROR_ACTIVE = auto()  # TEC/REC <= 127
    ERROR_PASSIVE = auto() # TEC/REC >= 128
    BUS_OFF = auto()       # TEC >= 256

class Role(Enum):
    NORMAL = auto() #ecu normale
    ATTACKER = auto() # ecu attaccante 

# ID speciale e type per simulare l'Error Frame sul bus
ERROR_FLAG_ID = 0x7E0
class ErrorFlagType(Enum):
    ACTIVE = 0  # 6 bit Dominanti
    PASSIVE = 1 # 6 bit Recessivi

# --- Classe Base ECU ---

class ECU:
    def __init__(
        self,
        name: str,
        role: Role,
        interface: str,
        arbitration_id: int,
        period_sec: float,
        initial_tec: int = 0,
        initial_rec: int = 0,
        self.tx_deadline = 0.0   # tempo entro cui mi aspetto un ERROR_FLAG
    ):
        self.name = name
        self.role = role
        self.iface = interface
        self.arb_id = arbitration_id
        self.period = period_sec

        self.tec = initial_tec
        self.rec = initial_rec
        self.state = NodeState.ERROR_ACTIVE
        self._update_state() # Inizializza lo stato

        self.currently_transmitting = False
        self.last_tx_data = None
        self.last_tx_time = 0.0

        # Configurazione SocketCAN (interface='socketcan')
        self.bus = can.interface.Bus(channel=self.iface, interface="socketcan", receive_own_messages=False)

        # Thread TX/RX
        self._stop = False
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        
        # Variabili specifiche per l'attacco (solo l'Attaccante le userà attivamente)
        self.is_under_attack = threading.Event()
        self.attack_detected_time = 0.0


    # -----------------------------------------------------
    # --- GESTIONE TEC/REC e STATI D'ERRORE ---
    # -----------------------------------------------------

    def _update_state(self):
        """Aggiorna lo stato dell'ECU in base ai contatori TEC/REC."""
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
        elif self.tec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    def _on_tx_success(self):
        """TEC diminuisce di 1 per trasmissione OK."""
        if self.tec > 0:
            self.tec -= 1
        self._update_state()

    def _on_tx_error(self):
        """
        Chiamato quando il nodo rileva un errore durante la sua trasmissione (TEC++).
        TEC aumenta di 8, ma 7 se è in ERROR_PASSIVE (come da specifiche del modello).
        """
        if self.state == NodeState.ERROR_ACTIVE:
            self.tec += 8
        elif self.state == NodeState.ERROR_PASSIVE:
            # Qui usiamo +7 per la Vittima/Normale, che è il modello di attacco (8 - 1).
            self.tec += 7 
        self._update_state()

    def _on_rx_error_flag(self):
        """
        Chiamato quando il nodo riceve un Error Frame (non stava trasmettendo).
        REGOLA: REC aumenta di 1.
        """
        self.rec += 1
        self._update_state()

    def _on_rx_success(self):
        """
        Chiamato quando il nodo riceve una trasmissione intera e CORRETTA.
        REGOLA: REC diminuisce di 1.
        """
        if self.rec > 0:
            self.rec -= 1
        self._update_state()

    # -----------------------------------------------------
    # --- GESTIONE ERROR FRAME (Risposta) ---
    # -----------------------------------------------------

    def _send_error_flag(self):
        """
        Invia la bandiera di errore appropriata allo stato corrente.
        """
        if self.state == NodeState.ERROR_ACTIVE:
            flag_type = ErrorFlagType.ACTIVE
        elif self.state == NodeState.ERROR_PASSIVE:
            flag_type = ErrorFlagType.PASSIVE
        else: # Bus Off
            return 
        
        data = bytearray(8)
        data[0] = flag_type.value 
        msg = can.Message(
            arbitration_id=ERROR_FLAG_ID,
            data=data,
            is_extended_id=False,
        )
        try:
            self.bus.send(msg)
            print(f"[{self.name}] --> ERROR_FLAG {flag_type.name} (TEC={self.tec}, REC={self.rec}, state={self.state.name})")
        except can.CanError as e:
            print(f"[{self.name}] Errore nell'invio error flag: {e}")


    # -----------------------------------------------------
    # --- LOOPS E COMUNICAZIONE ---
    # -----------------------------------------------------

    def _build_payload(self) -> bytes:
        """Payload generico (8 byte random)."""
        return bytes(random.randint(0, 255) for _ in range(8))

    def _tx_loop(self):
    """Loop periodico di trasmissione (per ECU NORMAL/VICTIM)."""
    next_tx = time.time()

    while not self._stop:
        if self.state == NodeState.BUS_OFF:
            print(f"[{self.name}] BUS OFF: Impossibile trasmettere. TEC={self.tec}")
            time.sleep(1.0)
            continue

        now = time.time()
        if self.period > 0 and now >= next_tx:
            payload = self._build_payload()
            msg = can.Message(
                arbitration_id=self.arb_id,
                data=payload,
                is_extended_id=False,
            )

            try:
                # Segno che sto trasmettendo
                self.currently_transmitting = True
                self.last_tx_data = payload
                self.last_tx_time = now

                # Finestra in cui mi aspetto un ERROR_FLAG (es. 20 ms)
                self.tx_deadline = now + 0.02

                self.bus.send(msg)
                print(f"[{self.name}] TX id=0x{self.arb_id:X} data={payload.hex().upper()} "
                      f"(state={self.state.name}, TEC={self.tec})")

                # ⚠️ NIENTE recv qui, niente _monitor_for_bit_error e niente _on_tx_*:
                #   - il successo/errore viene deciso da _rx_loop
                #   - se arriva un ERROR_FLAG mentre sto trasmettendo → _on_tx_error()
                #   - se NON arriva nulla entro tx_deadline → _on_tx_success()

            except can.CanError as e:
                print(f"[{self.name}] Errore invio frame: {e}")
                # Errore driver → consideralo errore TX
                self._on_tx_error()
                self.currently_transmitting = False

            next_tx += self.period

        time.sleep(0.02)

    def _monitor_for_bit_error(self) -> bool:
        """
        Ascolta immediatamente dopo la TX per rilevare se l'Attaccante ha causato un Bit Error.
        Questa è la simulazione del Bit Monitoring fallito.
        """
        # Timeout molto stretto (10ms)
        try:
            # L'Attaccante invia un frame con il nostro ID subito dopo il nostro invio
            attack_msg = self.bus.recv(timeout=0.01) 
            
            if attack_msg is not None and attack_msg.arbitration_id == self.arb_id:
                    if attack_msg.data != self.last_tx_data:
                        #Se un frame con il MIO ID è arrivato subito dopo il mio TX, 
                        # l'Attaccante ha causato un conflitto Bit Error.
                        print(f"[{self.name}] Rilevato messaggio in conflitto subito dopo TX.")
                
                        # Simula la generazione immediata dell'Error Frame 
                        self._send_error_flag()
                        return True
        
        except can.CanError:
            pass # Ignora errori di lettura bus
        return False
        
        
    def _rx_loop(self):
    """Loop di ricezione unico: gestisce ERROR_FLAG, bit error e RX normale."""
    while not self._stop:
        # 1) Gestione di TX in sospeso senza error frame → successo
        if self.currently_transmitting and time.time() > self.tx_deadline:
            # Non ho visto ERROR_FLAG entro la finestra → TX OK
            self._on_tx_success()
            print(f"[{self.name}] TX considerato SUCCESSO (no ERROR_FLAG entro deadline). TEC={self.tec}")
            self.currently_transmitting = False

        try:
            msg = self.bus.recv(timeout=0.05)
        except can.CanError as e:
            print(f"[{self.name}] Errore recv: {e}")
            continue

        if msg is None:
            continue

        # 2) ERROR FLAG (qualcuno ha segnalato un errore)
        if msg.arbitration_id == ERROR_FLAG_ID:
            flag_type = (
                ErrorFlagType(msg.data[0])
                if msg.data and msg.data[0] in (0, 1)
                else ErrorFlagType.ACTIVE
            )

            if self.currently_transmitting:
                # Ho rilevato un ERROR_FLAG mentre stavo trasmettendo → mio errore TX
                self._on_tx_error()
                self.currently_transmitting = False
                print(f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} mentre trasmette "
                      f"→ TEC={self.tec}, state={self.state.name}")
            else:
                # Sto solo ascoltando → errore di qualcun altro → REC++
                self._on_rx_error_flag()
                print(f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} da RX "
                      f"→ REC={self.rec}, state={self.state.name}")
            continue

        # 3) Bit error “alla Owen”: vedo un frame con il MIO ID ma dati diversi subito dopo il mio TX
        if (
            self.currently_transmitting
            and msg.arbitration_id == self.arb_id
            and msg.data != self.last_tx_data
        ):
            # Questo è il frame corrotto dell'attaccante
            print(f"[{self.name}] BIT ERROR: RX frame in conflitto con il mio TX.")
            # In CAN reale qui genererei i 6 bit dominanti → simuliamo con ERROR_FLAG
            self._send_error_flag()
            # _rx_loop vedrà poi l'ERROR_FLAG e chiamerà _on_tx_error()
            # quindi qui NON chiamiamo _on_tx_error() per evitare doppio incremento.
            continue

        # 4) Frame normale → RX successo (REC-- se >0)
        self._on_rx_success()
        self._handle_normal_frame(msg)

    def _handle_normal_frame(self, msg: can.Message):
        """Hook per la logica specifica del ruolo (Attacker)."""
        pass

    # ------------- API pubbliche ------------- #

    def start(self):
        print(f"[{self.name}] Avvio ECU (role={self.role.name}, id=0x{self.arb_id:X})")
        self.tx_thread.start()
        self.rx_thread.start()

    def stop(self):
        self._stop = True
        self.tx_thread.join(timeout=1.0)
        self.rx_thread.join(timeout=1.0)
        self.bus.shutdown()
        print(f"[{self.name}] Arrestata. TEC={self.tec}, REC={self.rec}, state={self.state.name}")
