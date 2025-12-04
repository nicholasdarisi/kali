# ecu_base.py

import can
import time
import threading
import random
from enum import Enum, auto

class NodeState(Enum):
    ERROR_ACTIVE = auto()
    ERROR_PASSIVE = auto()
    BUS_OFF = auto()

class Role(Enum):
    NORMAL = auto()
    VICTIM = auto()
    ATTACKER = auto()

# ID speciale usato per “simulare” un error frame su vcan0
ERROR_FLAG_ID = 0x7E0  # arbitrario ma fuori dal range che usi normalmente

class ErrorFlagType(Enum):
    ACTIVE = 0
    PASSIVE = 1

class ECU:
    def __init__(
        self,
        name: str,
        role: Role,
        interface: str,
        arbitration_id: int,
        period_sec: float,
        initial_tec: int = 0,
    ):
        self.name = name
        self.role = role
        self.iface = interface
        self.arb_id = arbitration_id
        self.period = period_sec

        self.tec = initial_tec
        self.rec = 0
        self.state = NodeState.ERROR_ACTIVE

        # Ultimo frame trasmesso (per confrontare con quello che ricevi)
        self.last_tx_data = None
        self.last_tx_time = 0.0

        # Flag molto semplificato: “in questa finestra di tempo sto trasmettendo”
        self.currently_transmitting = False

        # Config python-can
        self.bus = can.interface.Bus(channel=self.iface, bustype="socketcan")

        # Thread TX/RX
        self._stop = False
        self.tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

    # ------------- gestione TEC/REC e stati ------------- #

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
        elif self.tec >= 128 or self.rec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    def _on_tx_success(self):
        # semplificazione: se trasmissione ok, TEC diminuisce di 1
        if self.tec > 0:
            self.tec -= 1
        self._update_state()

    def _on_tx_error(self):
        # come da tue slide: +8 in ERROR_ACTIVE, +7 in ERROR_PASSIVE
        if self.state == NodeState.ERROR_ACTIVE:
            self.tec += 8
        elif self.state == NodeState.ERROR_PASSIVE:
            self.tec += 7
        self._update_state()

    def _on_rx_error_flag(self):
        # Nodo che non trasmette ma vede error frame → REC++
        self.rec += 1
        self._update_state()

    # ------------- gestione error flag simulati ------------- #

    def _send_error_flag(self, flag_type: ErrorFlagType):
        """
        Simula l’invio dei 6 bit dominanti / recessivi:
        in realtà manda un CAN frame speciale con ID ERROR_FLAG_ID
        che tutti gli altri interpretano come error frame.
        """
        data = bytearray(8)
        data[0] = flag_type.value  # 0 = ACTIVE, 1 = PASSIVE
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

    # ------------- payload generico ------------- #

    def _build_payload(self) -> bytes:
        """
        Payload generico per un ECU normale/vittima.
        Attaccante lo override-a per fare bit flip, ecc.
        """
        # 8 byte random giusto per non avere sempre gli stessi
        return bytes(random.randint(0, 255) for _ in range(8))

    # ------------- TX / RX loop ------------- #

    def _tx_loop(self):
        """
        Loop periodico di trasmissione.
        La VICTIM e la NORMAL ECU si comportano allo stesso modo qui.
        L’ATTACKER di solito *non* trasmette periodicamente, ma può farlo se vuoi.
        """
        next_tx = time.time()

        while not self._stop:
            if self.state == NodeState.BUS_OFF:
                # in BUS_OFF non trasmetti
                time.sleep(0.1)
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

                    self.bus.send(msg)
                    print(f"[{self.name}] TX id=0x{self.arb_id:X} data={payload.hex().upper()} (state={self.state.name}, TEC={self.tec}, REC={self.rec})")

                    # NB: nel modello “frame-level” questa trasmissione è
                    # sempre considerata “successo” finché non scopriamo
                    # un errore dalla RX (mismatch o error flag).
                    self._on_tx_success()

                except can.CanError as e:
                    print(f"[{self.name}] Errore invio frame: {e}")

                finally:
                    # piccola finestra in cui consideriamo "sto trasmettendo"
                    time.sleep(0.01)
                    self.currently_transmitting = False

                next_tx += self.period

            time.sleep(0.005)

    def _rx_loop(self):
        """
        Loop di ricezione:
        - vede i frame normali
        - vede eventuali ERROR_FLAG_ID e aggiorna REC/TEC
        - la VICTIM usa la RX per capire se è stata attaccata
        """
        while not self._stop:
            try:
                msg = self.bus.recv(timeout=0.1)
            except can.CanError as e:
                print(f"[{self.name}] Errore recv: {e}")
                continue

            if msg is None:
                continue

            # 1) Error frame simulato
            if msg.arbitration_id == ERROR_FLAG_ID:
                # qualcuno ha mandato un error flag
                flag_type = ErrorFlagType(msg.data[0]) if msg.data and msg.data[0] in (0, 1) else ErrorFlagType.ACTIVE

                if self.currently_transmitting:
                    # Nodo che stava trasmettendo e vede il suo stesso error flag
                    # (o comunque un error frame sincronizzato con la sua TX)
                    self._on_tx_error()
                    print(f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} mentre trasmette → TEC={self.tec}, state={self.state.name}")
                else:
                    # Nodo che non trasmette, quindi solo RX error
                    self._on_rx_error_flag()
                    print(f"[{self.name}] Rilevato ERROR_FLAG {flag_type.name} da RX → REC={self.rec}, state={self.state.name}")
                continue

            # 2) Frame normali → hook per comportamenti di ruolo
            self._handle_normal_frame(msg)

    # ------------- logica per frame normali (differenzia VICTIM/ATTACKER/NORMAL) ------------- #

    def _handle_normal_frame(self, msg: can.Message):
        """
        Comportamento base: ECU normale.
        VICTIM e ATTACKER override-ano parti di questa logica
        per fare detection dell’attacco o bit flip.
        """
        # Di default solo logga.
        print(f"[{self.name}] RX id=0x{msg.arbitration_id:X} data={msg.data.hex().upper()}")

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


class VictimECU(ECU):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _handle_normal_frame(self, msg: can.Message):
        # Log generico
        print(f"[{self.name}] RX id=0x{msg.arbitration_id:X} data={msg.data.hex().upper()}")

        # Se non è il mio stesso ID non mi interessa per l'attacco
        if msg.arbitration_id != self.arb_id:
            return

        # Controllo se è arrivato subito dopo un mio TX
        now = time.time()
        if self.last_tx_data is None:
            return

        # finestra temporale stretta (es: 20ms)
        if now - self.last_tx_time > 0.02:
            return

        # Se il payload è diverso da quello che ho trasmesso → ho subito un bit flip
        if msg.data != self.last_tx_data:
            print(f"[{self.name}] POSSIBILE ATTACCO: data TX={self.last_tx_data.hex().upper()} RX={msg.data.hex().upper()}")

            # Aggiorno TEC secondo le regole
            self._on_tx_error()

            # Genero il mio error flag attivo/passivo
            if self.state == NodeState.ERROR_ACTIVE:
                self._send_error_flag(ErrorFlagType.ACTIVE)
            elif self.state == NodeState.ERROR_PASSIVE:
                self._send_error_flag(ErrorFlagType.PASSIVE)

def flip_first_one_from_left(byte_val: int) -> int:
    """
    Cerca il primo bit a 1 da sinistra (bit 7 → 0) e lo mette a 0.
    Se il byte è 0x00, lo lascia invariato.
    """
    for bit in range(7, -1, -1):
        if byte_val & (1 << bit):
            return byte_val & ~(1 << bit)
    return byte_val


class AttackerECU(ECU):
    def __init__(self, victim_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.victim_id = victim_id

    # Attaccante di solito non trasmette periodicamente → override per disattivare TX loop
    def _tx_loop(self):
        while not self._stop:
            time.sleep(0.1)

    def _handle_normal_frame(self, msg: can.Message):
        """
        Sniffa il traffico.
        Se vede un frame della vittima, fa bit-flip sul primo byte e
        reinvia il frame corrotto.
        """
        print(f"[{self.name}] RX id=0x{msg.arbitration_id:X} data={msg.data.hex().upper()}")

        if msg.arbitration_id != self.victim_id:
            return

        # Costruisco i dati corrotti copiando l'originale
        data = bytearray(msg.data)
        if len(data) > 0:
            data[0] = flip_first_one_from_left(data[0])

        att_msg = can.Message(
            arbitration_id=msg.arbitration_id,
            data=data,
            is_extended_id=msg.is_extended_id
        )

        try:
            self.currently_transmitting = True
            self.last_tx_data = bytes(data)
            self.last_tx_time = time.time()

            self.bus.send(att_msg)
            print(f"[{self.name}] ATTACK: vittima={msg.data.hex().upper()} → attaccante={att_msg.data.hex().upper()}")

            # Anche l'attaccante, nel tuo modello, è una ECU “normale”:
            # quindi se poi rileva error flag mentre trasmette, TEC++,
            # secondo la logica già presente in ECU._rx_loop()

            # Trasmissione per ora considerata "ok"
            self._on_tx_success()

        except can.CanError as e:
            print(f"[{self.name}] Errore invio frame attacco: {e}")

        finally:
            time.sleep(0.01)
            self.currently_transmitting = False