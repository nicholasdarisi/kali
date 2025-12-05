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
        self.last_rx_id = None
        self.last_rx_time = 0.0

        # Configurazione SocketCAN (interface='socketcan')
        self.bus = can.interface.Bus(channel=self.iface, interface="socketcan", receive_own_messages=False)

        # Thread TX/RX
        self._stop = False
        self.collision_event = threading.Event()
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
        """Loop periodico di trasmissione (per ECU NORMAL / vittima)."""
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
                    self.currently_transmitting = True
                    self.last_tx_data = payload
                    self.last_tx_time = now
                    
                    # RESETTO l'evento di collisione prima di iniziare a trasmettere
                    self.collision_event.clear()
    
                    self.bus.send(msg)
                    print(f"[{self.name}] TX id=0x{self.arb_id:X} data={payload.hex().upper()} "
                          f"(state={self.state.name}, TEC={self.tec})")
    
                    # --- SINCRONIZZAZIONE ---
                    # Invece di leggere dal bus (che lo fa già rx_loop), aspetto un segnale.
                    # Se l'RX loop vede un attacco o un Error Flag entro 0.1s, sblocca questo wait.
                    
                    collision_occurred = self.collision_event.wait(timeout=0.1)
                    
                    if collision_occurred:
                        # RX Loop ha rilevato il problema e ha già chiamato _on_tx_error()
                        print(f"[{self.name}] TX fallita -> Collisione confermata dal RX loop.")
                    else:
                        # Nessuna notizia = Buona notizia. Nessun attacco rilevato nel timeout.
                        self._on_tx_success()
    
                except can.CanError as e:
                    print(f"[{self.name}] Errore invio frame (Driver): {e}")
                    self._on_tx_error()
    
                finally:
                    self.currently_transmitting = False
                    next_tx += self.period
    
            time.sleep(0.02)
        
        
    def _rx_loop(self):
        """Loop di ricezione e gestione degli Error Flags e Collisioni."""
        while not self._stop:
            try:
                # Timeout breve per permettere allo script di chiudersi se _stop diventa True
                msg = self.bus.recv(timeout=0.1)
            except can.CanError as e:
                print(f"[{self.name}] Errore recv: {e}")
                continue

            if msg is None:
                continue

            # ---------------------------------------------------------
            # 1) GESTIONE ERROR FRAME (Qualcuno ha segnalato errore)
            # ---------------------------------------------------------
            if msg.arbitration_id == ERROR_FLAG_ID:
                flag_type = ErrorFlagType(msg.data[0]) if msg.data and msg.data[0] in (0, 1) else ErrorFlagType.ACTIVE

                if self.currently_transmitting:
                    # Stavo trasmettendo e qualcuno mi ha segnalato errore -> Sono io il colpevole
                    self._on_tx_error()
                    print(f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} mentre trasmettevo -> TEC={self.tec}")
                    self._send_error_flag() # Rispondo con il mio flag
                    # Avviso il TX loop che c'è stato un errore esterno
                    self.collision_event.set()
                else:
                    # Ero in ascolto e qualcuno ha segnalato errore
                    self._on_rx_error_flag() # REC AUMENTA
                    print(f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} da RX -> REC={self.rec}")
                continue

            # ---------------------------------------------------------
            # 2) RILEVAMENTO ATTACCO (Collisione sul mio ID - Per la Vittima)
            # ---------------------------------------------------------
            if msg.arbitration_id == self.arb_id:
                print(f"[{self.name}] CRITICO: Rilevato messaggio ostile (Attacco) con mio ID. Data={msg.data.hex()}")
                self.collision_event.set()
                self._send_error_flag()
                self._on_tx_error() 
                continue

            # ---------------------------------------------------------
            # 3) FRAME NORMALI E FILTRO ANTI-FALSI SUCCESSI (Per la Terza ECU)
            # ---------------------------------------------------------
            now = time.time()
            
            # Controllo se è un duplicato ravvicinato (l'attacco che arriva subito dopo)
            is_collision_artifact = (
                self.last_rx_id is not None and 
                self.last_rx_id == msg.arbitration_id and 
                (now - self.last_rx_time) < 0.02 # 20ms finestra temporale
            )

            # Aggiorno memoria
            self.last_rx_id = msg.arbitration_id
            self.last_rx_time = now

            if is_collision_artifact:
                # È la copia corrotta/doppia generata dall'attacco. 
                # NON considerarlo successo, ma trattalo come errore (o rumore).
                print(f"[{self.name}] Ignorato frame duplicato (Collisione) -> REC AUMENTA")
                self._on_rx_error_flag() # REC +1
            else:
                # Messaggio pulito -> Successo
                self._on_rx_success() # REC -1
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
