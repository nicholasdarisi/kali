# ecu_base.py

import can
import time
import threading
import random
from enum import Enum, auto

# --- Definizione Stati e Ruoli ---

class NodeState(Enum):
    ERROR_ACTIVE = auto()   # TEC/REC <= 127
    ERROR_PASSIVE = auto()  # TEC/REC >= 128
    BUS_OFF = auto()        # TEC >= 256


class Role(Enum):
    NORMAL = auto()    # ECU normale / vittima
    ATTACKER = auto()  # ECU attaccante


# ID speciale e type per simulare l'Error Frame sul bus
ERROR_FLAG_ID = 0x7E0


class ErrorFlagType(Enum):
    ACTIVE = 0   # 6 bit Dominanti
    PASSIVE = 1  # 6 bit Recessivi


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
        self._update_state()  # Inizializza lo stato

        # Stato TX/RX
        self.currently_transmitting = False
        self.last_tx_data = None
        self.last_tx_time = 0.0

        # Per il modello "ritrasmetti lo stesso frame se sei stato attaccato"
        self.pending_payload = None

        # Per gestire il REC in modo coerente con eventuali collisioni
        self.last_rx_id = None
        self.last_rx_time = 0.0
        self.last_rx_decremented = False

        # Event usata per sincronizzare "TX ha avuto collisione"
        self.collision_event = threading.Event()

        # Configurazione SocketCAN
        self.bus = can.interface.Bus(
            channel=self.iface,
            interface="socketcan",
            receive_own_messages=False,
        )

        # Thread TX/RX
        self._stop = False
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

        # Variabili specifiche per scenari futuri (attacco, ecc.)
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
        - In ERROR_ACTIVE:  TEC += 8  (active error flag)
        - In ERROR_PASSIVE: TEC += 7  (8 di errore - 1 di 'successo' passivo sul bus)
        """
        if self.state == NodeState.ERROR_ACTIVE:
            self.tec += 8
        elif self.state == NodeState.ERROR_PASSIVE:
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
        ACTIVE → 6 bit dominanti
        PASSIVE → 6 bit recessivi
        """
        if self.state == NodeState.ERROR_ACTIVE:
            flag_type = ErrorFlagType.ACTIVE
        elif self.state == NodeState.ERROR_PASSIVE:
            flag_type = ErrorFlagType.PASSIVE
        else:  # BUS_OFF non genera error flag
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
            print(
                f"[{self.name}] --> ERROR_FLAG {flag_type.name} "
                f"(TEC={self.tec}, REC={self.rec}, state={self.state.name})"
            )
        except can.CanError as e:
            print(f"[{self.name}] Errore nell'invio error flag: {e}")

    # -----------------------------------------------------
    # --- LOOPS E COMUNICAZIONE ---
    # -----------------------------------------------------

    def _build_payload(self) -> bytes:
        """
        Costruisce un payload che rispetta lo schema "tipo CAN" che ci siamo dati:

        data[0]:
            bit 7 : RTR (0 = data frame)
            bit 6 : IDE (0 = standard)
            bit 5 : r0 (sempre 1 per le ECU normali/vittima)
            bit 3-0 : DLC (qui fisso a 8)

        data[1..7]: payload random (8 byte totali nel nostro modello).
        """
        # Header/control byte
        control = 0x00

        # RTR = 0 (bit 7)  -> già 0
        # IDE = 0 (bit 6)  -> già 0

        # r0 = 1 (bit 5)
        control |= (1 << 5)

        # DLC = 8 (0b1000) nei 4 bit meno significativi
        dlc = 8 & 0x0F
        control |= dlc

        payload = bytearray(8)
        payload[0] = control

        # Restante payload "dati applicativi"
        for i in range(1, 8):
            payload[i] = random.randint(0, 255)

        return bytes(payload)

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
                # --- Logica "ritrasmetti lo stesso frame se l'ultimo è fallito" ---
                if self.pending_payload is not None:
                    payload = self.pending_payload
                else:
                    payload = self._build_payload()
                    self.pending_payload = payload

                msg = can.Message(
                    arbitration_id=self.arb_id,
                    data=payload,
                    is_extended_id=False,
                )

                try:
                    self.currently_transmitting = True
                    self.last_tx_data = payload
                    self.last_tx_time = now

                    # prima di trasmettere, resetto l'evento di collisione
                    self.collision_event.clear()

                    self.bus.send(msg)
                    print(
                        f"[{self.name}] TX id=0x{self.arb_id:X} data={payload.hex().upper()} "
                        f"(state={self.state.name}, TEC={self.tec})"
                    )

                    # Aspetto che l'RX loop mi dica se è avvenuta una collisione/errore
                    collision_occurred = self.collision_event.wait(timeout=0.1)

                    if collision_occurred:
                        # _rx_loop ha già chiamato _on_tx_error()
                        print(f"[{self.name}] TX fallita (collisione / error flag).")
                        # NON tocco pending_payload → verrà ritentato identico
                    else:
                        # Nessun problema rilevato → TX OK
                        self._on_tx_success()
                        print(
                            f"[{self.name}] TX SUCCESSO → TEC={self.tec}, state={self.state.name}"
                        )
                        # Frame confermato → non serve più ritrasmetterlo
                        self.pending_payload = None

                except can.CanError as e:
                    print(f"[{self.name}] Errore invio frame (Driver): {e}")
                    self._on_tx_error()
                    # pending_payload rimane (ritenterò lo stesso frame)

                finally:
                    self.currently_transmitting = False
                    next_tx += self.period

            time.sleep(0.02)

    def _rx_loop(self):
        """Loop di ricezione e gestione degli Error Flags e collisioni."""
        while not self._stop:
            try:
                msg = self.bus.recv(timeout=0.1)
            except can.CanError:
                continue

            if msg is None:
                continue

            # ---------------------------------------------------------
            # 1) GESTIONE ERROR FRAME
            # ---------------------------------------------------------
            if msg.arbitration_id == ERROR_FLAG_ID:
                flag_type = (
                    ErrorFlagType(msg.data[0])
                    if msg.data and msg.data[0] in (0, 1)
                    else ErrorFlagType.ACTIVE
                )

                if self.currently_transmitting:
                    # Ho ricevuto (da un altro nodo) un error flag mentre trasmettevo
                    self._on_tx_error()
                    self.collision_event.set()
                    print(
                        f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} mentre trasmette "
                        f"→ TEC={self.tec}, state={self.state.name}"
                    )
                else:
                    # Sto solo ascoltando → errore di qualcun altro → REC++
                    self._on_rx_error_flag()
                    print(
                        f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} da RX "
                        f"→ REC={self.rec}, state={self.state.name}"
                    )
                continue

            # ---------------------------------------------------------
            # 2) RILEVAMENTO ATTACCO (frame con MIO ID ma dati diversi)
            #    → Simula il BIT ERROR sul campo r0
            # ---------------------------------------------------------
            if (
                self.currently_transmitting
                and msg.arbitration_id == self.arb_id
                and msg.data != self.last_tx_data
            ):
                # Questo è il frame dell'attaccante che ha modificato r0
                print(f"[{self.name}] BIT ERROR: RX frame in conflitto con il mio TX.")
                # Aggiorno subito TEC e segnalo collisione alla TX
                self._on_tx_error()
                self.collision_event.set()
                # In CAN reale qui genererei 6 bit dominanti/recessivi:
                self._send_error_flag()
                continue

            # ---------------------------------------------------------
            # 3) FRAME NORMALI (RX successo)
            # ---------------------------------------------------------
            now = time.time()

            is_collision_artifact = (
                self.last_rx_id is not None
                and self.last_rx_id == msg.arbitration_id
                and (now - self.last_rx_time) < 0.02
            )

            self.last_rx_id = msg.arbitration_id
            self.last_rx_time = now

            if is_collision_artifact:
                # Caso particolare: seconda copia "vicina" dello stesso ID.
                # Se prima avevamo considerato RX successo e avevamo decrementato REC,
                # qui ripristiniamo l'errore.
                if self.last_rx_decremented:
                    self._on_rx_error_flag()
                    print(
                        f"[{self.name}] Collisione RX -> REC ripristinato (era stato decrementato)."
                    )
                else:
                    print(
                        f"[{self.name}] Collisione RX -> REC invariato (era già a 0, non avevamo decrementato)."
                    )
                self.last_rx_decremented = False
            else:
                # RX normale → successo
                if self.rec > 0:
                    self.rec -= 1
                    self.last_rx_decremented = True
                else:
                    self.last_rx_decremented = False

                self._update_state()
                self._handle_normal_frame(msg)

    def _handle_normal_frame(self, msg: can.Message):
        """Hook per la logica specifica del ruolo (Attacker/ECU normale)."""
        # Le ECU normali di base non fanno nulla di speciale sul frame ricevuto.
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
        print(
            f"[{self.name}] Arrestata. TEC={self.tec}, REC={self.rec}, state={self.state.name}"
        )
