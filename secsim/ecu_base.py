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

# ID speciale per simulare gli Error Flag sul bus
ERROR_FLAG_ID = 0x7E0

class ErrorFlagType(Enum):
    ACTIVE = 0   # 6 bit dominanti
    PASSIVE = 1  # 6 bit recessivi


# ======================================================================
#                               ECU BASE
# ======================================================================

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

        # Contatori errore
        self.tec = initial_tec
        self.rec = initial_rec
        self.state = NodeState.ERROR_ACTIVE
        self._update_state()

        # Stato TX/RX
        self.currently_transmitting = False
        self.last_tx_data = None
        self.last_tx_time = 0.0

        # Stato RX per gestione REC “corretto”
        self.last_rx_id = None
        self.last_rx_time = 0.0
        self.last_rx_decremented = False

        # SocketCAN
        self.bus = can.interface.Bus(
            channel=self.iface,
            interface="socketcan",
            receive_own_messages=False,
        )

        # Thread
        self._stop = False
        self.collision_event = threading.Event()
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

        # Flag che userai solo se ti serve in estensioni future
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
        """Trasmissione terminata correttamente → TEC diminuisce di 1."""
        if self.tec > 0:
            self.tec -= 1
        self._update_state()

    def _on_tx_error(self):
        """
        Errore durante la *mia* trasmissione → TEC aumenta di 8.

        NOTA: qui NON facciamo +7 in error-passive.
        Il +7 della vittima in fase 2 viene fuori come:
            _on_tx_error()  →  TEC + 8
            _on_tx_success() → TEC - 1
        chiamati in sequenza quando il nodo è in ERROR_PASSIVE.
        """
        self.tec += 8
        self._update_state()

    def _on_rx_error_flag(self):
        """
        Ho ricevuto un Error Flag mentre stavo solo ascoltando.
        REC aumenta di 1.
        """
        self.rec += 1
        self._update_state()

    def _on_rx_success(self):
        """
        Ho ricevuto un frame valido e completo.
        REC diminuisce di 1 (se > 0).
        (Questa funzione è usata solo nella versione “semplice”;
         in questo file usiamo una variante esplicita dentro _rx_loop.)
        """
        if self.rec > 0:
            self.rec -= 1
        self._update_state()

    # -----------------------------------------------------
    # --- GESTIONE ERROR FRAME (INVIO) ---
    # -----------------------------------------------------

    def _send_error_flag(self):
        """
        Invia sul bus un Error Flag coerente con lo stato attuale.
        ERROR_ACTIVE  → 6 bit dominanti (ACTIVE)
        ERROR_PASSIVE → 6 bit recessivi (PASSIVE)
        BUS_OFF       → nessun flag.
        """
        if self.state == NodeState.ERROR_ACTIVE:
            flag_type = ErrorFlagType.ACTIVE
        elif self.state == NodeState.ERROR_PASSIVE:
            flag_type = ErrorFlagType.PASSIVE
        else:
            # BUS_OFF: non partecipa al traffico
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
        """Payload generico (8 byte random)."""
        return bytes(random.randint(0, 255) for _ in range(8))

    # -------------------- TX LOOP -------------------- #

    def _tx_loop(self):
        """Loop periodico di trasmissione (per ECU NORMAL/VITTIMA)."""
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

                    # Reset dell’evento collisione prima dell’invio
                    self.collision_event.clear()

                    self.bus.send(msg)
                    print(
                        f"[{self.name}] TX id=0x{self.arb_id:X} "
                        f"data={payload.hex().upper()} "
                        f"(state={self.state.name}, TEC={self.tec})"
                    )

                    # Attendo un eventuale errore segnalato da _rx_loop.
                    collision_occurred = self.collision_event.wait(timeout=0.1)

                    if collision_occurred:
                        # _rx_loop ha già chiamato _on_tx_error()
                        print(f"[{self.name}] TX fallita → collisione confermata dal RX loop.")
                    else:
                        # Nessun errore visto nel tempo di attesa → TX OK
                        self._on_tx_success()

                except can.CanError as e:
                    print(f"[{self.name}] Errore invio frame (Driver): {e}")
                    self._on_tx_error()

                finally:
                    self.currently_transmitting = False
                    next_tx += self.period

            time.sleep(0.02)

    # -------------------- RX LOOP -------------------- #

    def _rx_loop(self):
        """Loop di ricezione: gestisce ERROR_FLAG, collisioni e RX normali."""
        while not self._stop:
            try:
                msg = self.bus.recv(timeout=0.1)
            except can.CanError:
                continue

            if msg is None:
                continue

            # ---------------------------------------------------------
            # 1) GESTIONE ERROR FLAG RICEVUTI
            # ---------------------------------------------------------
            if msg.arbitration_id == ERROR_FLAG_ID:
                flag_type = (
                    ErrorFlagType(msg.data[0])
                    if msg.data and msg.data[0] in (0, 1)
                    else ErrorFlagType.ACTIVE
                )

                if self.currently_transmitting:
                    # ERRORE sulla MIA trasmissione (qualcun altro ha visto errore).
                    was_passive = (self.state == NodeState.ERROR_PASSIVE)

                    self._on_tx_error()           # TEC +8
                    if was_passive:
                        # Il mio passive error flag viene trasmesso correttamente
                        # → simuliamo TEC -1 (netto +7).
                        self._on_tx_success()

                    # Sblocco il TX loop
                    self.collision_event.set()

                    print(
                        f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} mentre trasmette "
                        f"→ TEC={self.tec}, state={self.state.name}"
                    )
                else:
                    # Sono un osservatore: vedo un errore di qualcun altro
                    if flag_type == ErrorFlagType.ACTIVE:
                        # Active error flag → errore reale sul bus → REC++
                        self._on_rx_error_flag()
                        print(
                            f"[{self.name}] ACTIVE Error Flag → REC +1 (Tot: {self.rec})"
                        )
                    else:
                        # Passive error flag → correzione del “falso errore” precedente
                        if self.rec > 0:
                            self.rec -= 1
                            self._update_state()
                        print(
                            f"[{self.name}] PASSIVE Error Flag → compensazione REC → {self.rec}"
                        )
                continue

            # ---------------------------------------------------------
            # 2) BIT ERROR ALLA CHO-SHIN: frame con MIO ID mentre TX
            #    (collisione con attaccante, C1–C3)
            # ---------------------------------------------------------
            if self.currently_transmitting and msg.arbitration_id == self.arb_id:
                # Qui puoi anche controllare msg.data != self.last_tx_data se vuoi
                # simulare esplicitamente il bit-flip.
                was_passive = (self.state == NodeState.ERROR_PASSIVE)

                print(f"[{self.name}] BIT ERROR: frame con mio ID durante TX.")
                # Genero il mio error flag (active/passive a seconda dello stato attuale)
                self._send_error_flag()

                # TEC +8 per errore TX
                self._on_tx_error()

                # Se ero già in error-passive, simulo il passive error flag riuscito → TEC -1
                if was_passive:
                    self._on_tx_success()

                # Segnalo collisione al TX loop
                self.collision_event.set()
                continue

            # ---------------------------------------------------------
            # 3) FRAME NORMALI (RX riuscito)
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
                # Secondo frame "duplicato" dopo collisione:
                # annullo il decremento di REC fatto sul primo.
                if self.last_rx_decremented:
                    self._on_rx_error_flag()  # REC +1 → annulla il -1 precedente
                    print(f"[{self.name}] Collisione → REC ripristinato (aveva decrementato).")
                else:
                    print(f"[{self.name}] Collisione → REC invariato (era già 0).")

                self.last_rx_decremented = False
            else:
                # Frame normale, nessuna collisione → RX successo
                if self.rec > 0:
                    self.rec -= 1
                    self.last_rx_decremented = True
                else:
                    self.last_rx_decremented = False

                self._update_state()
                self._handle_normal_frame(msg)

    # Hook da overridare in AttackerECU / ECU normali custom
    def _handle_normal_frame(self, msg: can.Message):
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
            f"[{self.name}] Arrestata. TEC={self.tec}, REC={self.rec}, "
            f"state={self.state.name}"
        )
