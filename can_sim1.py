"""
Simulazione CAN bit-level con master/slave, attacco su r0 e integrazione socketCAN.

Requisiti:
    pip install python-can

Su Linux crea l'interfaccia:
    sudo modprobe vcan
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0
e in un altro terminale:
    candump -td vcan0
"""

import time
import threading
import queue
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional

import can   # python-can


# ===================== ENUM E DATACLASS =====================

class BitValue(Enum):
    DOMINANT = 0  # 0
    RECESSIVE = 1  # 1


class NodeState(Enum):
    ERROR_ACTIVE = auto()
    ERROR_PASSIVE = auto()
    BUS_OFF = auto()


class MasterState(Enum):
    IDLE = auto()
    ARBITRATION = auto()
    TRANSMIT = auto()
    EOF = auto()
    INTERFRAME = auto()


@dataclass
class TransmissionRequest:
    slave_name: str
    slave_id: int
    arbitration_id: int
     bytes
    timestamp: float
    is_attacker: bool = False
    is_victim: bool = False


@dataclass
class BitTransmission:
    bit_value: BitValue
    timestamp: float
    sender_name: str
    logical_source: str  # 'VICTIM', 'ATTACKER', 'ECU'


# ===================== MASTER =====================

class CANMaster:
    """
    Master che simula il bus a livello bit, gestisce arbitraggio e inoltra
    i frame verso socketCAN (vcan0).
    """

    ERROR_FLAG_ID = 0x7E0  # ID riservato per error frame 'virtuali'

    def __init__(self, tick_ms: float = 0.5, forward_to_socketcan: bool = True,
                 can_channel: str = "vcan0"):
        self.tick = tick_ms / 1000.0
        self.state = MasterState.IDLE
        self.clock = 0

        self.slaves: Dict[int, "BaseECU"] = {}
        self.tx_requests: "queue.Queue[TransmissionRequest]" = queue.Queue()

        # coda bit distribuiti a ciascuno slave
        self.bit_queues: Dict[int, "queue.Queue[BitTransmission]"] = {}

        # frame attuale
        self.current_req: Optional[TransmissionRequest] = None
        self.current_bits: "queue.Queue[BitValue]" = queue.Queue()
        self.current_sender_slave_id: Optional[int] = None
        self.current_error_flag: Optional[NodeState] = None  # None / ERROR_ACTIVE / ERROR_PASSIVE

        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)

        # forwarding su socketCAN
        self.forward = forward_to_socketcan
        self.hw_bus: Optional[can.Bus] = None
        if self.forward:
            self.hw_bus = can.interface.Bus(
                channel=can_channel,
                interface="socketcan",
                receive_own_messages=False,
            )
            print(f"[MASTER] Collegato a socketCAN su {can_channel}")

    # ---------- API pubbliche ----------

    def register_slave(self, ecu: "BaseECU"):
        self.slaves[ecu.slave_id] = ecu
        self.bit_queues[ecu.slave_id] = queue.Queue()
        print(f"[MASTER] Registrata ECU {ecu.name} (slave_id={ecu.slave_id}, ID=0x{ecu.arb_id:X})")

    def submit_request(self, req: TransmissionRequest):
        print(f"[MASTER] Ricevuta richiesta TX da {req.slave_name} (ID=0x{req.arbitration_id:X})")
        self.tx_requests.put(req)

    def get_bit_for_slave(self, slave_id: int, timeout: float = 0.01) -> Optional[BitTransmission]:
        q = self.bit_queues.get(slave_id)
        if not q:
            return None
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    def start(self):
        print("[MASTER] Avvio master loop")
        self._thread.start()

    def stop(self):
        self._stop = True
        self._thread.join(timeout=2)
        print("[MASTER] Arrestato")

        if self.hw_bus is not None:
            self.hw_bus.shutdown()

    # ---------- LOOP MASTER ----------

    def _loop(self):
        while not self._stop:
            self.clock += 1

            if self.state == MasterState.IDLE:
                self._handle_idle()
            elif self.state == MasterState.ARBITRATION:
                self._handle_arbitration()
            elif self.state == MasterState.TRANSMIT:
                self._handle_transmit()
            elif self.state == MasterState.EOF:
                self._handle_eof()
            elif self.state == MasterState.INTERFRAME:
                self._handle_interframe()

            time.sleep(self.tick)

    # ---------- Stati ----------

    def _handle_idle(self):
        # Prende tutte le richieste pending in questo istante
        pending: List[TransmissionRequest] = []
        try:
            while True:
                req = self.tx_requests.get_nowait()
                pending.append(req)
        except queue.Empty:
            pass

        if not pending:
            return

        print(f"[MASTER] IDLE: {len(pending)} richieste di TX da gestire")

        # se c'è una sola richiesta: nessun arbitraggio
        if len(pending) == 1:
            self.current_req = pending[0]
            self.current_sender_slave_id = pending[0].slave_id
            print(f"[MASTER] Nessun arbitraggio: trasmetto {pending[0].slave_name}")
        else:
            # arbitraggio bit-per-bit sull'ID
            self.current_req = self._arbitrate(pending)
            self.current_sender_slave_id = self.current_req.slave_id

        # prepara i bit del frame
        self._prepare_bits_for_current_req()
        self.current_error_flag = None
        self.state = MasterState.TRANSMIT

    def _handle_arbitration(self):
        # (non usato: arbitraggio è fatto in _handle_idle per semplicità)
        pass

    def _handle_transmit(self):
        if self.current_req is None:
            self.state = MasterState.IDLE
            return

        try:
            bit = self.current_bits.get_nowait()
        except queue.Empty:
            # fine frame -> EOF
            print("[MASTER] Fine bit del frame logico, passo a EOF")
            self.state = MasterState.EOF
            return

        # trasmetti il bit sul "bus" e distribuisci agli slave
        bt = BitTransmission(
            bit_value=bit,
            timestamp=time.time(),
            sender_name=self.current_req.slave_name,
            logical_source=(
                "ATTACKER" if self.current_req.is_attacker
                else "VICTIM" if self.current_req.is_victim
                else "ECU"
            ),
        )
        self._broadcast_bit(bt)

    def _handle_eof(self):
        """
        Fine frame logico: qui decidiamo cosa inoltrare su socketCAN:
        - nessun errore -> data frame
        - errore ACTIVE -> solo error frame active
        - errore PASSIVE -> solo error frame passive
        """
        if self.current_req is None:
            self.state = MasterState.IDLE
            return

        req = self.current_req
        err_flag = self.current_error_flag

        if err_flag is None:
            print(f"[MASTER] EOF: frame di {req.slave_name} considerato OK → inoltro data frame su socketCAN")
            self._forward_data_frame(req)
        elif err_flag == NodeState.ERROR_ACTIVE:
            print(f"[MASTER] EOF: ERROR_ACTIVE rilevato → inoltro solo ERROR_FLAG_ACTIVE su socketCAN")
            self._forward_error_flag(NodeState.ERROR_ACTIVE, req)
        elif err_flag == NodeState.ERROR_PASSIVE:
            print(f"[MASTER] EOF: ERROR_PASSIVE rilevato → inoltro solo ERROR_FLAG_PASSIVE su socketCAN")
            self._forward_error_flag(NodeState.ERROR_PASSIVE, req)

        # interframe
        self.state = MasterState.INTERFRAME
        self._interframe_start = time.time()

    def _handle_interframe(self):
        # 3 * tick di pausa "simulata"
        if time.time() - self._interframe_start >= 3 * self.tick:
            print("[MASTER] Fine interframe → torno IDLE")
            self.current_req = None
            self.state = MasterState.IDLE

    # ---------- Arbitraggio ----------

    def _arbitrate(self, reqs: List[TransmissionRequest]) -> TransmissionRequest:
        """
        Arbitraggio bit-per-bit sugli 11 bit di ID.
        Vince l'ID numericamente più piccolo.
        """
        print("[MASTER] ARBITRAGGIO: candidati " +
              ", ".join(f"{r.slave_name}(ID=0x{r.arbitration_id:X})" for r in reqs))

        active = list(range(len(reqs)))  # indici dei candidati ancora in gioco

        for bit_pos in range(10, -1, -1):  # 11 bit: da MSB a LSB
            # per ciascun candidato, calcola il bit
            bits = []
            for i in active:
                rid = reqs[i].arbitration_id
                bit_val = (rid >> bit_pos) & 0x1
                bits.append((i, BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE))

            log_bits = ", ".join(
                f"{reqs[i].slave_name}:{'0' if b == BitValue.DOMINANT else '1'}"
                for (i, b) in bits
            )
            print(f"[MASTER]  ARB bit {bit_pos}: {log_bits}")

            # se tutti hanno stesso bit, nessuno viene scartato su questo bit
            if all(b == bits[0][1] for (_, b) in bits):
                continue

            # esiste almeno un 0 e almeno un 1 -> chi ha 1 perde
            active = [i for (i, b) in bits if b == BitValue.DOMINANT]

            if len(active) == 1:
                winner = reqs[active[0]]
                print(f"[MASTER]  → VINCITORE ARBITRAGGIO: {winner.slave_name} (ID=0x{winner.arbitration_id:X})")
                return winner

        # se arrivi qui, IDs uguali -> arbitraggio non discrimina
        winner = reqs[active[0]]
        print(f"[MASTER]  → IDs uguali, scelgo {winner.slave_name} (ID=0x{winner.arbitration_id:X})")
        return winner

    # ---------- Preparazione frame bit-level ----------

    def _prepare_bits_for_current_req(self):
        """
        Costruisce tutti i bit del frame CAN secondo il modello:
        SOF + ID11 + RTR + IDE + r0 + r1 + DLC4 + DATA + CRC15 + CRCdelim + ACK + EOF + IFS.
        r0/r1 sono fissati a recessive (1) nel modello ECU; l'attaccante li può forzare.
        """
        while not self.current_bits.empty():
            self.current_bits.get_nowait()

        req = self.current_req
        if req is None:
            return

        bits: List[BitValue] = []

        # SOF
        bits.append(BitValue.DOMINANT)

        # ID 11 bit
        for i in range(10, -1, -1):
            bit_val = (req.arbitration_id >> i) & 0x1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # RTR, IDE (entrambi 0 -> DOMINANT)
        bits.append(BitValue.DOMINANT)  # RTR
        bits.append(BitValue.DOMINANT)  # IDE

        # Control: r0, r1, DLC (qui: r0=1, r1=1, DLC= len(data) [4 bit])
        # QUI è il bit r0 che l'attaccante manipola: nel frame logico del master lo mettiamo 1,
        # l'attaccante in pratica modifica "sul bus" (vedi logica nello slave).
        bits.append(BitValue.RECESSIVE)  # r0 = 1
        bits.append(BitValue.RECESSIVE)  # r1 = 1
        dlc = len(req.data) & 0xF
        for i in range(3, -1, -1):
            bit_val = (dlc >> i) & 0x1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # Data bytes
        for b in req.
            for i in range(7, -1, -1):
                bit_val = (b >> i) & 0x1
                bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # CRC15 semplificato
        crc = self._calc_crc(req.arbitration_id, req.data)
        for i in range(14, -1, -1):
            bit_val = (crc >> i) & 0x1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # CRC delimiter
        bits.append(BitValue.RECESSIVE)

        # ACK slot + delimiter (il master manda recessive)
        bits.append(BitValue.RECESSIVE)
        bits.append(BitValue.RECESSIVE)

        # EOF 7 recessive
        for _ in range(7):
            bits.append(BitValue.RECESSIVE)

        # IFS 3 recessive
        for _ in range(3):
            bits.append(BitValue.RECESSIVE)

        print(f"[MASTER] Preparati {len(bits)} bit per {req.slave_name}")
        for b in bits:
            self.current_bits.put(b)

    @staticmethod
    def _calc_crc(arb_id: int,  bytes) -> int:
        # CRC semplificato, non conforme ma sufficiente per il modello
        crc = arb_id & 0x7FFF
        for b in 
            crc ^= b
            crc = ((crc << 1) ^ (0x4599 if (crc & 0x4000) else 0)) & 0x7FFF
        return crc

    # ---------- Broadcast e segnalazione errori ----------

    def _broadcast_bit(self, bt: BitTransmission):
        # log minimale per non floodare troppo
        # print(f"[MASTER] TX bit {bt.bit_value.name} by {bt.sender_name}")
        for sid, q in self.bit_queues.items():
            try:
                q.put_nowait(bt)
            except queue.Full:
                print(f"[MASTER] WARNING: coda bit piena per slave_id={sid}")

    def notify_error_flag_from_victim(self, victim: "BaseECU"):
        """
        Chiamata dalla vittima quando rileva un bit error.
        Aggiorna current_error_flag in base allo stato della vittima.
        """
        if victim.state == NodeState.ERROR_ACTIVE:
            self.current_error_flag = NodeState.ERROR_ACTIVE
        elif victim.state == NodeState.ERROR_PASSIVE:
            self.current_error_flag = NodeState.ERROR_PASSIVE
        # se BUS_OFF non genera flag

    # ---------- Forward verso socketCAN ----------

    def _forward_data_frame(self, req: TransmissionRequest):
        if self.hw_bus is None:
            return
        msg = can.Message(
            arbitration_id=req.arbitration_id,
            data=req.data,
            is_extended_id=False,
        )
        try:
            self.hw_bus.send(msg)
            print(f"[MASTER] → vcan0 DATA id=0x{req.arbitration_id:X} data={req.data.hex().upper()}")
        except can.CanError as e:
            print(f"[MASTER] Errore invio DATA su socketCAN: {e}")

    def _forward_error_flag(self, flag_state: NodeState, req: TransmissionRequest):
        if self.hw_bus is None:
            return
        # Modello: un frame con ID ERROR_FLAG_ID e data[0] = 0 ACTIVE, 1 PASSIVE
        data0 = 0 if flag_state == NodeState.ERROR_ACTIVE else 1
        msg = can.Message(
            arbitration_id=self.ERROR_FLAG_ID,
            data=bytes([data0]),
            is_extended_id=False,
        )
        try:
            self.hw_bus.send(msg)
            print(f"[MASTER] → vcan0 ERROR_FLAG {flag_state.name} (origine={req.slave_name})")
        except can.CanError as e:
            print(f"[MASTER] Errore invio ERROR_FLAG su socketCAN: {e}")


# ===================== ECU BASE =====================

class BaseECU:
    """
    ECU base (può essere normale o vittima). Simula TEC/REC e TX periodica.
    """

    def __init__(self, name: str, slave_id: int, arb_id: int,
                 master: CANMaster, period_sec: float,
                 is_victim: bool = False):
        self.name = name
        self.slave_id = slave_id
        self.arb_id = arb_id
        self.master = master
        self.period = period_sec
        self.is_victim = is_victim

        self.state = NodeState.ERROR_ACTIVE
        self.tec = 0
        self.rec = 0

        self._stop = False
        self._tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

        self.currently_transmitting = False
        self.last_req: Optional[TransmissionRequest] = None

        self.received_bits: List[BitTransmission] = []

        self.master.register_slave(self)

    # ----- gestione stato errore -----

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
        elif self.tec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    def _on_tx_success(self):
        if self.tec > 0:
            self.tec -= 1
        self._update_state()

    def _on_tx_error(self):
        if self.state == NodeState.ERROR_ACTIVE:
            self.tec += 8
        elif self.state == NodeState.ERROR_PASSIVE:
            self.tec += 7
        self._update_state()

    def _on_rx_error_flag(self):
        self.rec += 1
        self._update_state()

    # ----- API -----

    def start(self):
        print(f"[{self.name}] Avvio ECU (ID=0x{self.arb_id:X}, victim={self.is_victim})")
        self._tx_thread.start()
        self._rx_thread.start()

    def stop(self):
        self._stop = True
        self._tx_thread.join(timeout=1)
        self._rx_thread.join(timeout=1)
        print(f"[{self.name}] Arrestata (TEC={self.tec}, REC={self.rec}, state={self.state.name})")

    # ----- TX / RX -----

    def _tx_loop(self):
        next_tx = time.time() + random.uniform(0.0, 0.5)  # piccolo jitter
        while not self._stop:
            if self.state == NodeState.BUS_OFF:
                time.sleep(1.0)
                continue

            now = time.time()
            if self.period > 0 and now >= next_tx:
                data = self._build_payload()
                req = TransmissionRequest(
                    slave_name=self.name,
                    slave_id=self.slave_id,
                    arbitration_id=self.arb_id,
                    data=data,
                    timestamp=now,
                    is_attacker=False,
                    is_victim=self.is_victim,
                )
                self.last_req = req
                self.currently_transmitting = True
                print(f"[{self.name}] Richiedo TX data={data.hex().upper()} (state={self.state.name}, TEC={self.tec})")
                self.master.submit_request(req)
                # aspetta un po', poi assume TX success (o error gestito dal master/vittima)
                time.sleep(self.period * 0.3)
                if self.last_req is req and self.state != NodeState.BUS_OFF:
                    # semplificazione: se non è stato marcato errore altrove, consideriamo success
                    self._on_tx_success()
                    print(f"[{self.name}] TX SUCCESS (TEC={self.tec}, state={self.state.name})")
                self.currently_transmitting = False
                next_tx += self.period

            time.sleep(0.01)

    def _rx_loop(self):
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, timeout=0.05)
            if bt is None:
                continue
            # per ECU normali/vittima, qui registriamo solo i bit.
            self.received_bits.append(bt)
            # la logica speciale di errore su r0 è implementata nella Vittima (subclass)
            time.sleep(0.001)

    def _build_payload(self) -> bytes:
        # primo byte come "control" generico, ma in questo modello
        # il vero r0 è nel bit-stream, non nel payload.
        payload = bytearray(8)
        for i in range(8):
            payload[i] = random.randint(0, 255)
        return bytes(payload)


# ===================== ECU VITTIMA =====================

class VictimECU(BaseECU):
    """
    Vittima: oltre al comportamento base, controlla il bit r0 durante la TX.
    Quando vede un bit sul bus diverso da quello che "crede" di trasmettere,
    genera error flag ACTIVE/PASSIVE e aggiorna TEC.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # posizione del bit r0 nel frame: 
        # SOF (1) + ID(11) + RTR(1) + IDE(1) = 14 -> r0 è il bit logico index14
        self._bit_index_when_transmitting = -1

    def _rx_loop(self):
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, timeout=0.05)
            if bt is None:
                continue

            self.received_bits.append(bt)

            # Se siamo noi che stiamo trasmettendo, controlliamo i bit
            if self.currently_transmitting and self.last_req is not None:
                self._bit_index_when_transmitting += 1

                # controllo solo sul r0 (index 14)
                if self._bit_index_when_transmitting == 14:
                    # r0: la vittima crede di trasmettere RECESSIVE (1)
                    expected = BitValue.RECESSIVE
                    actual = bt.bit_value
                    if actual != expected:
                        print(f"[{self.name}] BIT ERROR su r0: expected={expected.name}, actual={actual.name}")
                        # genera error flag a seconda dello stato
                        old_state = self.state
                        self._on_tx_error()  # TEC +8/+7 e update state
                        print(f"[{self.name}] → TEC dopo errore: {self.tec}, state {old_state.name}→{self.state.name}")
                        self.master.notify_error_flag_from_victim(self)
                        # NB: non facciamo vero "inserimento" di 6 bit, lo modelliamo via current_error_flag
                        # Il master non inoltrerà il data frame, ma solo error flag su socketCAN.

            time.sleep(0.001)

    def _tx_loop(self):
        # override per resettare il bit index ad ogni TX
        next_tx = time.time() + random.uniform(0.0, 0.5)
        while not self._stop:
            if self.state == NodeState.BUS_OFF:
                time.sleep(1.0)
                continue

            now = time.time()
            if self.period > 0 and now >= next_tx:
                data = self._build_payload()
                req = TransmissionRequest(
                    slave_name=self.name,
                    slave_id=self.slave_id,
                    arbitration_id=self.arb_id,
                    data=data,
                    timestamp=now,
                    is_attacker=False,
                    is_victim=True,
                )
                self.last_req = req
                self.currently_transmitting = True
                self._bit_index_when_transmitting = -1
                print(f"[{self.name}] (VITTIMA) Richiedo TX data={data.hex().upper()} (state={self.state.name}, TEC={self.tec})")
                self.master.submit_request(req)
                time.sleep(self.period * 0.3)

                # Caso particolare: se l'attaccante ha continuato la TX in ERROR_PASSIVE,
                # la vittima vede il frame con il suo ID andare su bus e "crede" sia il suo:
                # a quel punto riduce TEC di 1 (modello semplificato).
                # Qui per semplicità: se current_error_flag è ERROR_PASSIVE e il master
                # ha comunque inoltrato un DATA frame con il nostro ID, consideriamo TX SUCCESS.
                if self.state != NodeState.BUS_OFF:
                    self._on_tx_success()
                    print(f"[{self.name}] (VITTIMA) Considera TX SUCCESS (TEC={self.tec}, state={self.state.name})")

                self.currently_transmitting = False
                next_tx += self.period

            time.sleep(0.01)


# ===================== ECU ATTACCANTE =====================

class AttackerECU(BaseECU):
    """
    Attaccante: stesso ID della vittima. Durante r0 forza il bit a DOMINANT
    e continua la trasmissione.

    - Quando la vittima è ERROR_ACTIVE: genera ERROR_FLAG_ACTIVE,
      frame scartato dal master → solo error frame su socketCAN.
    - Quando la vittima è ERROR_PASSIVE: genera ERROR_FLAG_PASSIVE, ma
      l'attaccante continua e il master inoltra il DATA frame con quell'ID.
      TEC_attacker-- per TX success.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bit_index = -1

    def _rx_loop(self):
        # L'attaccante riceve i bit dal master, ma usa anche un suo "shadow"
        # della trasmissione per decidere quando forzare r0 a DOMINANT.
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, timeout=0.05)
            if bt is None:
                continue

            self.received_bits.append(bt)

            if self.currently_transmitting and self.last_req is not None:
                self._bit_index += 1

                # Quando arriviamo al bit r0 (index 14), l'attaccante
                # forza 0 (DOMINANT) "sul bus".
                if self._bit_index == 14:
                    print(f"[{self.name}] FORZA r0=DOMINANT (attacco)")
                    # nel modello: il master ha già generato il bit logico (RECESSIVE),
                    # ma noi vogliamo che sul bus appaia DOMINANT, quindi:
                    # sovrascriviamo l'ultimo BitTransmission in tutte le code
                    self._force_last_bit_dominant()

            time.sleep(0.001)

    def _force_last_bit_dominant(self):
        """
        Modello semplificato: prendiamo l'ultimo bit consegnato a ciascuno slave
        e lo trasformiamo in DOMINANT. In un simulatore più preciso questo
        sarebbe gestito nel master, ma per illustrare l'attacco basta così.
        """
        for sid, q in self.master.bit_queues.items():
            # rimpiazza l'ultimo elemento in coda, se presente
            tmp: List[BitTransmission] = []
            while not q.empty():
                tmp.append(q.get_nowait())
            if not tmp:
                continue
            last = tmp[-1]
            overridden = BitTransmission(
                bit_value=BitValue.DOMINANT,
                timestamp=last.timestamp,
                sender_name=self.name,
                logical_source="ATTACKER",
            )
            tmp[-1] = overridden
            for el in tmp:
                q.put_nowait(el)

    def _tx_loop(self):
        # Attaccante trasmette con stessa period della vittima (per provocare collisione)
        next_tx = time.time() + random.uniform(0.0, 0.5)
        while not self._stop:
            if self.state == NodeState.BUS_OFF:
                time.sleep(1.0)
                continue

            now = time.time()
            if self.period > 0 and now >= next_tx:
                data = self._build_payload()
                req = TransmissionRequest(
                    slave_name=self.name,
                    slave_id=self.slave_id,
                    arbitration_id=self.arb_id,
                    data=data,
                    timestamp=now,
                    is_attacker=True,
                    is_victim=False,
                )
                self.last_req = req
                self.currently_transmitting = True
                self._bit_index = -1
                print(f"[{self.name}] (ATTACCANTE) Richiedo TX data={data.hex().upper()} (state={self.state.name}, TEC={self.tec})")
                self.master.submit_request(req)
                time.sleep(self.period * 0.3)

                # L'attaccante, dal suo punto di vista, considera:
                # - se la vittima era ERROR_ACTIVE: anche lui subisce errore → TEC+8
                #   (questo lo possiamo modellare usando _on_tx_error, ma qui per semplicità
                #   lo lasciamo alla logica del test/manuale).
                # - se la vittima è ERROR_PASSIVE: il frame "va a buon fine" → TEC-1
                if self.state != NodeState.BUS_OFF:
                    self._on_tx_success()
                    print(f"[{self.name}] (ATTACCANTE) TX SUCCESS (TEC={self.tec}, state={self.state.name})")

                self.currently_transmitting = False
                next_tx += self.period

            time.sleep(0.01)


# ===================== SCENARIO DI TEST =====================

def main():
    """
    Scenario:
    - ECU_A e ECU_B con ID diversi trasmettono quasi insieme → vedi arbitraggio.
    - Victim e Attacker con stesso ID, stesso periodo → attacco su r0:
      prima in ERROR_ACTIVE, poi in ERROR_PASSIVE.
    """
    master = CANMaster(tick_ms=0.5, forward_to_socketcan=True, can_channel="vcan0")

    # ECU normali per mostrare arbitraggio
    ecu_a = BaseECU("ECU_A", slave_id=1, arb_id=0x100, master=master, period_sec=3.0)
    ecu_b = BaseECU("ECU_B", slave_id=2, arb_id=0x200, master=master, period_sec=3.0)

    # Vittima e attaccante con stesso ID
    victim = VictimECU("VICTIM", slave_id=10, arb_id=0x123, master=master, period_sec=2.0, is_victim=True)
    attacker = AttackerECU("ATTACKER", slave_id=11, arb_id=0x123, master=master, period_sec=2.0)

    master.start()
    ecu_a.start()
    ecu_b.start()
    victim.start()
    attacker.start()

    try:
        for sec in range(40):
            time.sleep(1.0)
            print(f"\n[STATUS @ {sec+1}s]")
            for ecu in (ecu_a, ecu_b, victim, attacker):
                print(f"  {ecu.name}: TEC={ecu.tec:3d}, REC={ecu.rec:3d}, state={ecu.state.name}")
    except KeyboardInterrupt:
        print("Interrotto da tastiera.")
    finally:
        ecu_a.stop()
        ecu_b.stop()
        victim.stop()
        attacker.stop()
        master.stop()


if __name__ == "__main__":
    main()
