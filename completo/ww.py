"""
Weeping CAN Attack Simulator con analisi bit-level e reinforcement learning
"""

import threading
import time
import random
from collections import defaultdict
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
import can
from enum import Enum, auto
from typing import List, Optional, Tuple
from dataclasses import dataclass

# --- Bit Value ---
class BitValue(Enum):
    DOMINANT = 0
    RECESSIVE = 1

    @staticmethod
    def from_int(v: int) -> "BitValue":
        return BitValue.DOMINANT if v == 0 else BitValue.RECESSIVE

    def __int__(self) -> int:
        return 0 if self is BitValue.DOMINANT else 1


class NodeState(Enum):
    ERROR_ACTIVE = auto()
    ERROR_PASSIVE = auto()
    BUS_OFF = auto()


class Field(Enum):
    SOF = auto()
    ID = auto()
    RTR = auto()
    IDE = auto()
    R0 = auto()
    DLC = auto()
    DATA = auto()
    CRC = auto()
    CRC_DELIM = auto()
    ACK_SLOT = auto()
    ACK_DELIM = auto()
    EOF = auto()
    INTERMISSION = auto()
    STUFF = auto()


@dataclass
class BitTransmission:
    bit_value: BitValue
    timestamp: float
    sender_name: str
    field: Field


def _crc15_can(bits: List[int]) -> int:
    """Compute CRC-15/CAN over a bit stream."""
    poly = 0x4599
    crc = 0
    for b in bits:
        msb = (crc >> 14) & 1
        crc = ((crc << 1) & 0x7FFF) | (b & 1)
        if msb:
            crc ^= poly
    return crc & 0x7FFF


class CANBitStream:
    """Build a *stuffed* CAN base frame bit stream and per-bit field labels."""

    def __init__(self, arbitration_id: int, data: bytes, r0: BitValue = BitValue.RECESSIVE):
        self.arb_id = arbitration_id & 0x7FF
        self.data = data[:8]
        self.r0 = r0

        self.bits: List[BitValue] = []
        self.fields: List[Field] = []
        self._build()

    def _push(self, bit: BitValue, field: Field):
        self.bits.append(bit)
        self.fields.append(field)

    def _build_unstuffed_payload_bits(self) -> Tuple[List[BitValue], List[Field]]:
        bits: List[BitValue] = []
        fields: List[Field] = []

        def push(bit: BitValue, field: Field):
            bits.append(bit)
            fields.append(field)

        # SOF
        push(BitValue.DOMINANT, Field.SOF)

        # 11-bit ID (MSB first)
        for i in range(10, -1, -1):
            push(BitValue.from_int((self.arb_id >> i) & 1), Field.ID)

        # Control field (base frame)
        push(BitValue.DOMINANT, Field.RTR)
        push(BitValue.DOMINANT, Field.IDE)
        push(self.r0, Field.R0)

        # DLC 4 bits
        dlc = len(self.data)
        for i in range(3, -1, -1):
            push(BitValue.from_int((dlc >> i) & 1), Field.DLC)

        # DATA bytes
        for byte in self.data:
            for i in range(7, -1, -1):
                push(BitValue.from_int((byte >> i) & 1), Field.DATA)

        # CRC
        crc_input = [int(b) for b in bits]
        crc = _crc15_can(crc_input)
        for i in range(14, -1, -1):
            push(BitValue.from_int((crc >> i) & 1), Field.CRC)

        # CRC delimiter
        push(BitValue.RECESSIVE, Field.CRC_DELIM)
        # ACK slot
        push(BitValue.RECESSIVE, Field.ACK_SLOT)
        push(BitValue.RECESSIVE, Field.ACK_DELIM)
        # EOF 7 recessive
        for _ in range(7):
            push(BitValue.RECESSIVE, Field.EOF)
        # Intermission 3 recessive
        for _ in range(3):
            push(BitValue.RECESSIVE, Field.INTERMISSION)

        return bits, fields

    @staticmethod
    def _apply_bit_stuffing(
        bits: List[BitValue], fields: List[Field]
    ) -> Tuple[List[BitValue], List[Field]]:
        """Stuff from SOF through end of CRC sequence (inclusive)."""
        out_bits: List[BitValue] = []
        out_fields: List[Field] = []

        run_val: Optional[BitValue] = None
        run_len = 0

        def should_stuff(idx: int) -> bool:
            return fields[idx] in {
                Field.SOF,
                Field.ID,
                Field.RTR,
                Field.IDE,
                Field.R0,
                Field.DLC,
                Field.DATA,
                Field.CRC,
            }

        for idx, (b, f) in enumerate(zip(bits, fields)):
            out_bits.append(b)
            out_fields.append(f)

            if not should_stuff(idx):
                run_val = None
                run_len = 0
                continue

            if run_val is None:
                run_val = b
                run_len = 1
            else:
                if b == run_val:
                    run_len += 1
                    if run_len == 5:
                        stuffed = BitValue.RECESSIVE if run_val is BitValue.DOMINANT else BitValue.DOMINANT
                        out_bits.append(stuffed)
                        out_fields.append(Field.STUFF)
                        run_val = stuffed
                        run_len = 1
                else:
                    run_val = b
                    run_len = 1

        return out_bits, out_fields

    def _build(self):
        raw_bits, raw_fields = self._build_unstuffed_payload_bits()
        stuffed_bits, stuffed_fields = self._apply_bit_stuffing(raw_bits, raw_fields)
        self.bits = stuffed_bits
        self.fields = stuffed_fields


def bytes_to_bits(data: bytes) -> List[int]:
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


# --- CAN Bus Master ---
class CANBusMaster:
    """
    Simulatore semplificato:
    - arbitra frame tra più ECU
    - gestisce collisioni (stesso ID) e invia error flag active anche su vcan0
    """
    def __init__(self, use_vcan: bool = False):
        self.ecus = {}
        self.pending = []
        self.lock = threading.Lock()
        self._stop = False
        self._thread = None
        self.collect_window = 0.002
        self.use_vcan = use_vcan
        self.vcan_bus = None
        if self.use_vcan:
            try:
                self.vcan_bus = can.interface.Bus(channel='vcan0', interface='socketcan')
                print("[MASTER] Connected to vcan0")
            except Exception as e:
                print(f"[MASTER] Error connecting to vcan0: {e}")
                self.vcan_bus = None

    def register_ecu(self, ecu):
        self.ecus[ecu.slave_id] = ecu

    def submit_transmission(self, ecu, data: bytes, arb_id: int, r0: BitValue = BitValue.RECESSIVE):
        with self.lock:
            self.pending.append((ecu, data, arb_id, r0))

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True
        try:
            if self.vcan_bus is not None:
                self.vcan_bus.shutdown()
        except Exception:
            pass

    def _run(self):
        while not self._stop:
            with self.lock:
                if not self.pending:
                    pass
                else:
                    contenders = self.pending[:]
                    self.pending.clear()
                    self._process_contenders(contenders)
            time.sleep(self.collect_window)

    def _process_contenders(self, contenders):
        if len(contenders) == 1:
            ecu, data, arb_id, r0 = contenders[0]
            if ecu.is_bus_off():
                return
            self._transmit_frame(ecu, data, arb_id, r0, contenders)
            return

        contenders = [c for c in contenders if not c[0].is_bus_off()]
        if not contenders:
            return

        winner = self._perform_arbitration(contenders)
        if winner is None or winner[0] is None:
            return

        winner_ecu, winner_data, winner_id, winner_r0 = winner
        self._transmit_frame(winner_ecu, winner_data, winner_id, winner_r0, contenders)

    def _perform_arbitration(self, contenders):
        """Esegue l'arbitraggio bit-by-bit tra le ECU contendenti.

        contenders: List[(ecu, data, arb_id, r0)]
        """
        bitstreams = []
        for ecu, data, arb_id, r0 in contenders:
            bs = CANBitStream(arb_id, data, r0=r0)
            bitstreams.append((ecu, bs, arb_id, data, r0))

        active = list(range(len(bitstreams)))
        bit_idx = 0

        while len(active) > 1:
            if bit_idx >= min(len(bitstreams[i][1].bits) for i in active):
                break

            offered = []
            for i in active:
                ecu, bs, _, _, _ = bitstreams[i]
                if bit_idx < len(bs.bits):
                    bit = bs.bits[bit_idx]
                    field = bs.fields[bit_idx]
                    offered.append((i, ecu, bit, field))

            if not offered:
                break

            bus_bit = BitValue.DOMINANT if any(bit is BitValue.DOMINANT for _, _, bit, _ in offered) else BitValue.RECESSIVE
            field = offered[0][3]

            contenders_str = " | ".join([f"{ecu.name}={int(bit)}" for _, ecu, bit, _ in offered])
            print(f"  [ARB] {field.name:12s} | {contenders_str} -> BUS={int(bus_bit)}")

            # Durante l'arbitraggio ID, chi mette recessivo perde
            if field in {Field.SOF, Field.ID, Field.RTR}:
                losers = []
                for i, ecu, bit, _ in offered:
                    if bit is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
                        print(f"  [ARB] {ecu.name} perde arbitraggio")
                        losers.append(i)

                for loser_idx in sorted(losers, reverse=True):
                    if loser_idx in active:
                        active.remove(loser_idx)

            bit_idx += 1

            # Se stesso ID, continua con i dati/controllo: collisione volontaria (attacco)
            if field == Field.RTR and len(active) > 1:
                print(f"[MASTER] COLLISION! Stesso ID tra: {', '.join([bitstreams[i][0].name for i in active])}")
                return self._handle_collision(bitstreams, active, bit_idx)

        if len(active) == 1:
            winner_idx = active[0]
            winner_ecu, _, winner_id, winner_data, winner_r0 = bitstreams[winner_idx]
            print(f"[MASTER] WINNER: {winner_ecu.name} (ID=0x{winner_id:03X}) -> TRANSMIT")
            return winner_ecu, winner_data, winner_id, winner_r0

        return None, None, None, None

    def _handle_collision(self, bitstreams, active, start_bit_idx):
        """Gestisce collisione tra ECU con stesso ID (bit monitoring -> error flag)."""
        bit_idx = start_bit_idx
        error_detected = False
        offender_ecu = None

        while len(active) > 0 and not error_detected:
            offered = []
            for i in active:
                ecu, bs, _, _, _ = bitstreams[i]
                if bit_idx < len(bs.bits):
                    bit = bs.bits[bit_idx]
                    field = bs.fields[bit_idx]
                    offered.append((i, ecu, bit, field))

            if not offered:
                break

            bus_bit = BitValue.DOMINANT if any(bit is BitValue.DOMINANT for _, _, bit, _ in offered) else BitValue.RECESSIVE
            field = offered[0][3]

            contenders_str = " | ".join([f"{ecu.name}={int(bit)}" for _, ecu, bit, _ in offered])
            print(f"  [TX]  {field.name:12s} | {contenders_str} -> BUS={int(bus_bit)}")

            # Bit monitoring: se una ECU mette recessivo ma legge dominante -> ERROR
            for _, ecu, bit, _ in offered:
                if bit is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
                    if field not in {Field.SOF, Field.ID, Field.RTR}:
                        print(f"[MASTER] BIT ERROR rilevato da {ecu.name} (offender=bit_monitoring) -> error flag, frame abortito")
                        error_detected = True
                        offender_ecu = ecu
                        break

            bit_idx += 1

        if error_detected and offender_ecu:
            self._send_error_flag(offender_ecu)

            # Incrementa TEC di tutte le ECU coinvolte nella collisione:
            # - ECU in ERROR-ACTIVE: +8
            # - ECU in ERROR-PASSIVE: +7 (modello: +8 errore, ma -1 'successo' del passive flag => +7 netto)
            for i in active:
                ecu = bitstreams[i][0]
                inc = 7 if ecu.state is NodeState.ERROR_PASSIVE else 8
                ecu.tec += inc
                ecu._update_state()
                flag = "PASSIVE" if inc == 7 else "ACTIVE"
                print(f"[MASTER] {ecu.name}: TEC={ecu.tec} (+{inc} per errore {flag}) State={ecu.state.name}")

            # Incrementa REC dei listener
            involved = [bitstreams[i][0] for i in active]
            for ecu in self.ecus.values():
                if ecu not in involved and not ecu.is_bus_off():
                    ecu.rec += 1
                    print(f"[MASTER] {ecu.name}: REC={ecu.rec} (+1 per errore ricevuto)")

        return None, None, None, None

    def _send_error_flag_active(self, offender_ecu):
        """Invia error flag active (6 bit dominanti)"""
        print(f"\n[MASTER] Sending ERROR FLAG ACTIVE (6 dominant bits)")

        for bit_num in range(6):
            print(f"  [ERR] ERROR_FLAG_ACTIVE | {offender_ecu.name} -> BUS=0 (bit {bit_num+1}/6)")

        if self.use_vcan:
            try:
                error_msg = can.Message(
                    arbitration_id=0x7FF,
                    data=[0x00] * 6,
                    is_extended_id=False
                )
                self.vcan_bus.send(error_msg)
                print(f"[MASTER] Error Active Flag sent to vcan0")
            except Exception as e:
                print(f"[MASTER] Error sending error flag to vcan0: {e}")

    def _send_error_flag_passive(self, offender_ecu):
        """Invia error flag passive (8 bit recessivi)."""
        print(f"\n[MASTER] Sending ERROR FLAG PASSIVE (8 recessive bits)")
        for bit_num in range(8):
            print(f"  [ERR] ERROR_FLAG_PASSIVE | {offender_ecu.name} -> BUS=1 (bit {bit_num+1}/8)")
        # Nota: su SocketCAN non inviamo un vero error-frame; qui è solo logging.

    def _send_error_flag(self, offender_ecu):
        """Invia error flag coerente con lo stato dell'offender."""
        if offender_ecu.state is NodeState.ERROR_PASSIVE:
            self._send_error_flag_passive(offender_ecu)
        else:
            self._send_error_flag_active(offender_ecu)

    def _transmit_frame(self, winner_ecu, data, arb_id, r0, all_contenders):
        """Trasmette il frame vincente"""
        bs = CANBitStream(arb_id, data, r0=r0)

        for bit, field in zip(bs.bits, bs.fields):
            print(f"  [TX]  {field.name:12s} | {winner_ecu.name}={int(bit)}")

        print(f"[MASTER] Frame OK: ID=0x{arb_id:03X} data={data.hex().upper()}")

        if self.use_vcan:
            try:
                msg = can.Message(
                    arbitration_id=arb_id,
                    data=data,
                    is_extended_id=False
                )
                self.vcan_bus.send(msg)
            except Exception as e:
                print(f"[MASTER] Error sending to vcan0: {e}")

        # TEC -= 1 per il vincitore (modello semplificato usato nel simulatore)
        winner_ecu.tec = max(0, winner_ecu.tec - 1)
        winner_ecu._update_state()
        print(f"[MASTER] {winner_ecu.name}: TEC={winner_ecu.tec} (-1 per successo) State={winner_ecu.state.name}")

        # REC -= 1 per i listener
        for ecu in self.ecus.values():
            if ecu != winner_ecu and not ecu.is_bus_off() and ecu.rec > 0:
                ecu.rec -= 1


# --- Base ECU ---
class BaseECU:
    def __init__(self, name: str, slave_id: int, arb_id: int, master: CANBusMaster,
                 tx_period: float = 3.0, start_delay: float = 0.0):
        self.name = name
        self.slave_id = slave_id
        self.arb_id = arb_id & 0x7FF
        self.master = master
        self.tx_period = tx_period
        self.start_delay = start_delay

        self.tec = 0
        self.rec = 0
        self.state = NodeState.ERROR_ACTIVE

        self.next_tx_time = 0.0
        self._stop = False
        self._tx_thread = None

        # per rendere l'analisi dei bit "sensata", usiamo un payload semi-deterministico:
        # molti bit stabili + un counter (gli ultimi 2 byte)
        self._counter = 0
        self.random_payload = False  # se vuoi proprio random: set True

        self.master.register_ecu(self)

    def start(self):
        print(f"[{self.name}] START slave_id={self.slave_id} ID=0x{self.arb_id:03X} period={self.tx_period:.2f}s")
        self.next_tx_time = time.time() + self.start_delay
        self._tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self._tx_thread.start()

    def stop(self):
        self._stop = True

    def is_bus_off(self) -> bool:
        return self.state is NodeState.BUS_OFF

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
            print(f"[{self.name}] *** ENTERED BUS-OFF STATE *** (TEC={self.tec})")
        elif self.tec >= 128:
            if self.state != NodeState.ERROR_PASSIVE:
                self.state = NodeState.ERROR_PASSIVE
                print(f"[{self.name}] Entered ERROR-PASSIVE state (TEC={self.tec})")
        else:
            self.state = NodeState.ERROR_ACTIVE

    def get_time_until_tx(self) -> float:
        return max(0.0, self.next_tx_time - time.time())

    def _build_payload(self) -> bytes:
        if self.random_payload:
            return bytes(random.randint(0, 255) for _ in range(8))

        c = self._counter & 0xFFFF
        self._counter = (self._counter + 1) & 0xFFFF

        # 6 byte "stabili" + 2 byte counter
        p = bytearray(8)
        p[0] = (self.arb_id >> 3) & 0xFF
        p[1] = self.arb_id & 0xFF
        p[2] = self.slave_id & 0xFF
        p[3] = 0xA5
        p[4] = 0x5A
        p[5] = 0xC3
        p[6] = (c >> 8) & 0xFF
        p[7] = c & 0xFF
        return bytes(p)

    def _tx_loop(self):
        # loop con sleep fine -> la vittima è molto più "periodica" e l'attacker si sincronizza meglio
        while not self._stop:
            if self.is_bus_off():
                time.sleep(0.01)
                continue

            now = time.time()
            dt = self.next_tx_time - now

            if dt <= 0:
                data = self._build_payload()
                print(f"[{self.name}] VUOLE TRASMETTERE (ID=0x{self.arb_id:03X}) TEC={self.tec} REC={self.rec} State={self.state.name}")
                self.master.submit_transmission(self, data, self.arb_id, r0=BitValue.RECESSIVE)

                # schedule senza drift (mantiene periodo costante)
                self.next_tx_time += self.tx_period
                # se eravamo in ritardo tanto, "recupera"
                while self.next_tx_time <= now:
                    self.next_tx_time += self.tx_period

                continue

            time.sleep(min(dt, 0.005))


# --- Weeping Attacker ---
class WeepingAttacker:
    def __init__(self, master: CANBusMaster, sniff_duration_1=150, sniff_duration_2=30):
        self.name = "ATTACKER"
        self.slave_id = 999
        self.master = master
        self.sniff_duration_1 = sniff_duration_1  # 75% training
        self.sniff_duration_2 = sniff_duration_2  # 25% reinforcement

        self.tec = 0
        self.rec = 0
        self.state = NodeState.ERROR_ACTIVE

        self.running = False
        self.attack_state = "sniffing_1"  # sniffing_1, analyzing, sniffing_2, reinforcement, attacking

        # Sniffing data
        self.sniffed_data_1 = defaultdict(list)
        self.sniffed_data_2 = defaultdict(list)
        self.min_sniffed_id = None

        self.seen_ids = set()
        self.reset_id = None

        # Victim
        self.victim_id = None
        self.victim_ecu = None
        self.victim_messages = []
        self.victim_bit_probabilities = []
        self.avg_interval = None
        self.last_victim_time = None
        self.next_attack_time = None

        # --- Anti flood / anti self-collision ---
        self._last_attacked_cycle_ts: Optional[float] = None
        self._pending_cycle_ts: Optional[float] = None

        # Attack params
        self.attack_r0 = BitValue.RECESSIVE          # R0=0 (dominant) per forzare mismatch (victim usa R0=1 recessive)
        self.reset_frames_per_round = 3             # (non usato direttamente: _reduce_tec usa 1..3)

        self._thread = None
        self._vcan_listener_thread = None
        self._stop = False

        # Dedicated socketCAN listener (do NOT reuse master's socket)
        self.sniff_bus = None
        if self.master.use_vcan:
            try:
                self.sniff_bus = can.interface.Bus(channel='vcan0', interface='socketcan')
                print("[ATTACKER] Connected dedicated sniff socket to vcan0")
            except Exception as e:
                print(f"[ATTACKER] Error connecting dedicated sniff socket to vcan0: {e}")
                self.sniff_bus = None

        self.master.register_ecu(self)

    def start(self):
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

        self._vcan_listener_thread = threading.Thread(target=self._vcan_listener, daemon=True)
        self._vcan_listener_thread.start()

    def stop(self):
        self.running = False
        self._stop = True
        try:
            if self.sniff_bus is not None:
                self.sniff_bus.shutdown()
        except Exception:
            pass

    def is_bus_off(self) -> bool:
        return self.state is NodeState.BUS_OFF

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
            print(f"[ATTACKER] *** ENTERED BUS-OFF STATE *** (TEC={self.tec})")
        elif self.tec >= 128:
            if self.state != NodeState.ERROR_PASSIVE:
                self.state = NodeState.ERROR_PASSIVE
                print(f"[ATTACKER] Entered ERROR-PASSIVE state (TEC={self.tec})")
        else:
            self.state = NodeState.ERROR_ACTIVE

    def get_time_until_tx(self) -> float:
        return 999.0  # Non trasmette periodicamente

    @property
    def arb_id(self):
        if self.attack_state == "attacking" and self.victim_id:
            return self.victim_id
        return 0x7FF

    def _vcan_listener(self):
        """Sniffa da vcan0 (solo frame *davvero* trasmessi su SocketCAN)."""
        if not self.master.use_vcan or self.sniff_bus is None:
            return

        print("[ATTACKER] Started vcan0 listener")

        while not self._stop:
            try:
                msg = self.sniff_bus.recv(timeout=1.0)

                # Live victim timing update (se arrivano frame reali su vcan0)
                if msg and self.victim_id is not None and msg.arbitration_id == self.victim_id:
                    self.last_victim_time = time.time()

                if msg and self.attack_state == "sniffing_1":
                    frame_data = bytes(msg.data)
                    frame_bits = bytes_to_bits(frame_data)

                    ts = time.time()
                    self.sniffed_data_1[msg.arbitration_id].append({
                        'data': frame_data,
                        'bits': frame_bits,
                        'timestamp': ts
                    })

                    self.seen_ids.add(msg.arbitration_id)

                    if self.min_sniffed_id is None or msg.arbitration_id < self.min_sniffed_id:
                        self.min_sniffed_id = msg.arbitration_id

                    data_hex = ' '.join([f'{b:02X}' for b in frame_data])
                    print(f"[ATTACKER SNIFF-1] ID=0x{msg.arbitration_id:03X} Data=[{data_hex}]")

                elif msg and self.attack_state == "sniffing_2" and msg.arbitration_id == self.victim_id:
                    frame_data = bytes(msg.data)
                    frame_bits = bytes_to_bits(frame_data)

                    self.sniffed_data_2[msg.arbitration_id].append({
                        'data': frame_data,
                        'bits': frame_bits,
                        'timestamp': time.time()
                    })

                    data_hex = ' '.join([f'{b:02X}' for b in frame_data])
                    print(f"[ATTACKER SNIFF-2] ID=0x{msg.arbitration_id:03X} Data=[{data_hex}]")

            except Exception:
                pass

    def _run(self):
        # Phase 1: Sniffing (Training)
        print(f"\n{'='*100}")
        print(f"[ATTACKER] PHASE 1: SNIFFING (Training) for {self.sniff_duration_1} seconds...")
        print(f"{'='*100}\n")

        sniff_start = time.time()
        while time.time() - sniff_start < self.sniff_duration_1:
            time.sleep(5)
            if len(self.sniffed_data_1) > 0:
                total_msgs = sum(len(msgs) for msgs in self.sniffed_data_1.values())
                print(f"[ATTACKER] Sniffed {total_msgs} messages from {len(self.sniffed_data_1)} different IDs")

        # Phase 2: Analysis
        print(f"\n{'='*100}")
        print(f"[ATTACKER] PHASE 2: ANALYZING sniffed data...")
        print(f"{'='*100}\n")

        self.attack_state = "analyzing"
        self._select_victim()

        if self.victim_id is None:
            print("[ATTACKER] ❌ No suitable victim found. Aborting.")
            self.running = False
            return

        if len(self.victim_messages) < 2:
            print(f"[ATTACKER] ❌ Not enough messages from victim (found {len(self.victim_messages)}). Aborting.")
            self.running = False
            return

        self._analyze_victim_bits()

        if not self.victim_bit_probabilities:
            print("[ATTACKER] ❌ Analysis failed. Aborting.")
            self.running = False
            return

        # Phase 3: Sniffing 2 (Reinforcement)
        print(f"\n{'='*100}")
        print(f"[ATTACKER] PHASE 3: SNIFFING (Reinforcement) for {self.sniff_duration_2} seconds...")
        print(f"{'='*100}\n")

        self.attack_state = "sniffing_2"
        sniff_start_2 = time.time()
        while time.time() - sniff_start_2 < self.sniff_duration_2:
            time.sleep(2)
            if self.victim_id in self.sniffed_data_2:
                print(f"[ATTACKER] Collected {len(self.sniffed_data_2[self.victim_id])} reinforcement messages")

        # Phase 4: Reinforcement Learning
        print(f"\n{'='*100}")
        print(f"[ATTACKER] PHASE 4: REINFORCEMENT LEARNING...")
        print(f"{'='*100}\n")

        self.attack_state = "reinforcement"
        self._reinforcement_learning()

        # Phase 5: Attack
        print(f"\n{'='*100}")
        print(f"[ATTACKER] 🎯 ATTACCO INIZIATO! 🎯")
        print(f"[ATTACKER] Target: ID=0x{self.victim_id:03X}")
        if self.avg_interval is not None:
            print(f"[ATTACKER] Average interval: {self.avg_interval:.3f}s")
        print(f"[ATTACKER] Strategy: send SAME ID + R0=0 (dominant) to force bit-monitoring error on R0")
        print(f"{'='*100}\n")

        self.attack_state = "attacking"
        self._attack_loop()

    def _estimate_interval(self, timestamps):
        """Stima robusta dell'intervallo di trasmissione usando mediana + filtro outlier."""
        if not timestamps or len(timestamps) < 2:
            return None
        ts = sorted(timestamps)
        intervals = [ts[i+1] - ts[i] for i in range(len(ts)-1)]
        intervals = [x for x in intervals if x > 0.0005]
        if not intervals:
            return None
        med = float(np.median(intervals))
        kept = [x for x in intervals if 0.5 * med <= x <= 1.5 * med]
        if len(kept) >= 2:
            return float(np.mean(kept))
        return med

    def _select_victim(self):
        """Seleziona la vittima (ID che trasmette più frequentemente)."""
        if not self.sniffed_data_1:
            print("[ATTACKER] ❌ No data sniffed during phase 1")
            return

        self.victim_id = max(self.sniffed_data_1, key=lambda k: len(self.sniffed_data_1[k]))
        self.victim_messages = self.sniffed_data_1[self.victim_id]

        # Trova riferimento all'ECU reale
        self.victim_ecu = None
        for ecu in self.master.ecus.values():
            if getattr(ecu, 'arb_id', None) == self.victim_id and getattr(ecu, 'name', '') != self.name:
                self.victim_ecu = ecu
                break

        print(f"[ATTACKER] ✓ Selected victim: ID=0x{self.victim_id:03X}")
        print(f"[ATTACKER] ✓ Total messages: {len(self.victim_messages)}")

        # FIX timing: se abbiamo il riferimento della ECU nel simulatore, usiamo direttamente il suo tx_period
        if self.victim_ecu is not None:
            self.avg_interval = float(self.victim_ecu.tx_period)
            self.next_attack_time = float(getattr(self.victim_ecu, "next_tx_time", time.time() + self.avg_interval))
            print(f"[ATTACKER] ✓ Using VICTIM tx_period (ground truth): {self.avg_interval:.3f}s")
            return

        # fallback: stima da vcan sniffing
        if len(self.victim_messages) > 1:
            timestamps = [msg['timestamp'] for msg in self.victim_messages]
            self.avg_interval = self._estimate_interval(timestamps)
            self.last_victim_time = max(timestamps) if timestamps else None
            self.next_attack_time = (self.last_victim_time + self.avg_interval) if (self.last_victim_time is not None and self.avg_interval is not None) else None

            if self.avg_interval is not None:
                print(f"[ATTACKER] ✓ Average transmission interval: {self.avg_interval:.3f}s (robust)")
            else:
                print("[ATTACKER] ⚠️ Could not estimate interval")
        else:
            print(f"[ATTACKER] ⚠️ Only {len(self.victim_messages)} message(s) found for victim")
            self.victim_id = None

    def _analyze_victim_bits(self):
        """Analizza i bit dei messaggi della vittima e calcola le probabilità."""
        if not self.victim_messages:
            print("[ATTACKER] ❌ No victim messages to analyze")
            return

        print(f"\n[ATTACKER] Analyzing bit patterns of victim {hex(self.victim_id)}...")

        all_bits = [msg['bits'] for msg in self.victim_messages]

        if not all(len(bits) == len(all_bits[0]) for bits in all_bits):
            print("[ATTACKER] ⚠️ Messages have different lengths, using minimum length")
            min_len = min(len(bits) for bits in all_bits)
            all_bits = [bits[:min_len] for bits in all_bits]

        num_bits = len(all_bits[0])

        self.victim_bit_probabilities = []
        for bit_pos in range(num_bits):
            bit_values = [bits[bit_pos] for bits in all_bits]
            prob_zero = sum(1 for b in bit_values if b == 0) / len(bit_values)
            prob_one = 1 - prob_zero
            self.victim_bit_probabilities.append({
                'position': bit_pos,
                'prob_0': prob_zero,
                'prob_1': prob_one
            })

        print(f"\n[ATTACKER] Bit probability analysis (top 10 most predictable):")
        print(f"{'='*80}")

        sorted_probs = sorted(
            self.victim_bit_probabilities,
            key=lambda x: max(x['prob_0'], x['prob_1']),
            reverse=True
        )

        for prob in sorted_probs[:10]:
            byte_idx = prob['position'] // 8
            bit_idx = 7 - (prob['position'] % 8)

            if prob['prob_0'] > prob['prob_1']:
                print(f"  Bit {prob['position']:2d} (Byte {byte_idx}, Bit {bit_idx}): "
                      f"{prob['prob_0']*100:.1f}% sempre 0 (DOMINANT)")
            else:
                print(f"  Bit {prob['position']:2d} (Byte {byte_idx}, Bit {bit_idx}): "
                      f"{prob['prob_1']*100:.1f}% sempre 1 (RECESSIVE)")

        print(f"{'='*80}\n")

    def _reinforcement_learning(self):
        """Reinforcement learning: verifica predizioni e aggiusta probabilità."""
        if self.victim_id not in self.sniffed_data_2 or len(self.sniffed_data_2[self.victim_id]) == 0:
            print("[ATTACKER] ⚠️ No reinforcement data collected. Skipping reinforcement.")
            return

        reinforcement_messages = self.sniffed_data_2[self.victim_id]

        print(f"[ATTACKER] Verifying predictions on {len(reinforcement_messages)} messages...")

        correct_predictions = 0
        total_bits = 0

        for msg in reinforcement_messages:
            bits = msg['bits']
            for prob in self.victim_bit_probabilities:
                pos = prob['position']
                if pos < len(bits):
                    predicted = 0 if prob['prob_0'] > prob['prob_1'] else 1
                    actual = bits[pos]
                    if predicted == actual:
                        correct_predictions += 1
                    total_bits += 1

        if total_bits > 0:
            accuracy = correct_predictions / total_bits * 100
            print(f"[ATTACKER] Prediction accuracy: {accuracy:.2f}%")
        else:
            print("[ATTACKER] No bits to verify.")

    def _wait_for_victim_transmission(self):
        """Aspetta fino al momento in cui la vittima sta per trasmettere."""
        lead = 0.0005

        # Se abbiamo riferimento ECU, usa next_tx_time (ground truth) con guard-rail.
        if self.victim_ecu is not None:
            while self.running and not self.is_bus_off():
                if self.victim_ecu.is_bus_off():
                    return

                now = time.time()
                nxt = float(getattr(self.victim_ecu, "next_tx_time", now + 0.01))
                dt = nxt - now
                cycle_ts = nxt

                if dt <= lead:
                    if self._last_attacked_cycle_ts is not None and abs(cycle_ts - self._last_attacked_cycle_ts) < 1e-6:
                        time.sleep(0.001)
                        continue
                    self._pending_cycle_ts = cycle_ts
                    return

                time.sleep(min(max(0.0, dt - lead), 0.01))
            return

        # fallback su next_attack_time
        if self.avg_interval is None:
            time.sleep(0.2)
            return

        if self.last_victim_time is not None:
            self.next_attack_time = self.last_victim_time + self.avg_interval

        if self.next_attack_time is None:
            time.sleep(0.2)
            return

        while self.running and not self.is_bus_off():
            now = time.time()
            dt = self.next_attack_time - now - lead
            if dt <= 0:
                break
            time.sleep(min(dt, 0.01))

        self.next_attack_time += self.avg_interval

    def _reduce_tec(self, num_messages: int = None):
        """Riduce il TEC inviando frame 'innocui' con ID basso (priorità alta).

        Requisiti:
        - ID variabile ad ogni frame (non sempre lo stesso), mantenendo comunque priorità alta (ID basso).
        - 1..3 frame per round (se num_messages non specificato).
        - payload completamente random (8 byte indipendenti ad ogni invio).
        """

        if num_messages is None:
            num_messages = random.randint(1, 3)
        else:
            num_messages = int(num_messages)

        # ID da evitare (best effort): quelli osservati durante sniffing + victim.
        observed = set(self.seen_ids) if self.seen_ids else set()
        if self.victim_id is not None:
            observed.add(self.victim_id)

        # Range di ID ad alta priorità: [0x010, upper] con upper < victim_id per restare prioritari.
        if self.victim_id is not None:
            upper = max(0x010, min(int(self.victim_id) - 1, 0x1FF))
        else:
            upper = 0x1FF

        # Cursore per cambiare ID ad ogni invio.
        if getattr(self, "_reset_id_cursor", None) is None:
            base = int(self.victim_id) - random.randint(1, 5) if self.victim_id is not None else 0x100
            self._reset_id_cursor = max(0x010, min(base, upper))

        def pick_next_id() -> int:
            # Avanza di un passo pseudo-random (1..5) e trova un ID non osservato (best effort).
            for _ in range(64):
                step = random.randint(1, 5)
                cand = self._reset_id_cursor + step
                if cand > upper:
                    span = max(1, (upper - 0x010 + 1))
                    cand = 0x010 + ((cand - 0x010) % span)
                self._reset_id_cursor = cand
                if cand not in observed:
                    return cand
            return int(self._reset_id_cursor)

        # Non rubare la finestra della vittima e non fare burst troppo aggressivi.
        if self.victim_ecu is not None:
            period = float(getattr(self.victim_ecu, "tx_period", 3.0))
            gap = max(0.03, min(0.20, (0.7 * period) / max(1, num_messages)))
        else:
            gap = 0.05

        for _ in range(num_messages):
            if self.victim_ecu is not None and self.victim_ecu.get_time_until_tx() <= (self.master.collect_window * 2.5 + gap):
                break

            reset_id = pick_next_id()
            reset_data = bytes(random.randint(0, 255) for _ in range(8))
            self.master.submit_transmission(self, reset_data, reset_id, r0=BitValue.RECESSIVE)
            time.sleep(gap)

    def _create_attack_message(self) -> bytes:
        """Crea il payload dell'attacco (campo DATA, 8 byte) usando le probabilità stimate.

        Strategia (lightweight learning):
        - Da victim_bit_probabilities (posizione 0..63, prob_0/prob_1, opzionale 'weight') costruiamo un payload
          "predetto" bit-a-bit (MAP): bit=0 se prob_0>=prob_1 altrimenti 1.
        - Scegliamo poi UN solo bit target dove la vittima ha massima probabilità di inviare 0
          (massimizza prob_0 * weight, se 'weight' esiste; altrimenti solo prob_0).
        - Flippiamo quel bit a 1 (0→1) così l'attaccante differisce dalla vittima solo in quel punto.
        """
        # Default: se non ho info, payload aggressivo (tutto 0)
        probs0 = [0.5] * 64
        probs1 = [0.5] * 64
        weights = [1.0] * 64

        if self.victim_bit_probabilities:
            for d in self.victim_bit_probabilities:
                try:
                    pos = int(d.get('position', 0))
                except Exception:
                    continue
                if 0 <= pos < 64:
                    p0 = float(d.get('prob_0', 0.5))
                    p1 = float(d.get('prob_1', 0.5))
                    s = p0 + p1
                    if s > 0:
                        p0, p1 = p0 / s, p1 / s
                    probs0[pos] = max(0.0, min(1.0, p0))
                    probs1[pos] = max(0.0, min(1.0, p1))
                    w = d.get('weight', 1.0)
                    try:
                        weights[pos] = max(0.01, float(w))
                    except Exception:
                        weights[pos] = 1.0

        # 1) Predizione MAP del payload vittima (pos 0 è MSB del byte 0)
        predicted_bits = [0 if probs0[i] >= probs1[i] else 1 for i in range(64)]

        # 2) Selezione bit target: max P0 * weight, ma solo se il payload predetto ha 0 in quel bit
        best_pos = None
        best_score = -1.0
        for i in range(64):
            if predicted_bits[i] == 0:
                score = probs0[i] * weights[i]
                if score > best_score:
                    best_score = score
                    best_pos = i

        # 3) Flippa il bit target 0→1
        if best_pos is not None:
            predicted_bits[best_pos] = 1
            byte_idx = best_pos // 8
            bit_idx = 7 - (best_pos % 8)
            conf0 = probs0[best_pos] * 100.0
            print(f"[ATTACKER] 🎯 Target DATA bit {best_pos} (Byte {byte_idx}, Bit {bit_idx}): "
                  f"P0≈{conf0:.1f}% | score={best_score:.3f} -> flip to 1")
        else:
            print("[ATTACKER] (warn) Nessun bit predetto a 0: uso payload tutto 0.")

        # 4) Pack bits -> 8 bytes (MSB-first)
        payload = bytearray(8)
        for pos in range(64):
            if predicted_bits[pos]:
                b = pos // 8
                k = 7 - (pos % 8)
                payload[b] |= (1 << k)

        return bytes(payload)

    def _attack_loop(self):
        """Loop principale dell'attacco: collide ad OGNI tentativo della vittima."""
        attack_count = 0

        while self.running and not self.is_bus_off():
            if self.victim_ecu is not None and self.victim_ecu.is_bus_off():
                return

            # Aspetta finestra della vittima
            self._wait_for_victim_transmission()
            if not self.running:
                break

            # marca il ciclo (per evitare multi-submit prima che la vittima aggiorni next_tx_time)
            if self._pending_cycle_ts is not None:
                self._last_attacked_cycle_ts = self._pending_cycle_ts
                self._pending_cycle_ts = None

            attack_count += 1
            print(f"\n{'='*60}")
            print(f"[ATTACKER] 🎯 ATTACK #{attack_count} on victim {hex(self.victim_id)}")
            print(f"{'='*60}")

            attack_data = self._create_attack_message()

            # Sottometti attacco: stesso ID + R0 DOMINANT (0)
            self.master.submit_transmission(self, attack_data, self.victim_id, r0=self.attack_r0)

            # Dai tempo al master di processare collisione
            time.sleep(0.05)

            # Abbassa TEC dell'attacker senza disturbare la prossima TX della vittima
            if self.tec > 0:
                print(f"[ATTACKER] ⚠️ Reducing TEC after attack (current: {self.tec}) ...")
                self._reduce_tec()

            time.sleep(0.01)


# --- Main ---
def main():
    print("="*100)
    print("WEEPING CAN ATTACK SIMULATOR - BIT-LEVEL ANALYSIS + REINFORCEMENT LEARNING")
    print("="*100)

    master = CANBusMaster(use_vcan=True)
    master.start()

    # Create ECUs
    ecu_a = BaseECU("ECU_A", 1, 0x100, master, tx_period=5.0, start_delay=2.0)
    ecu_b = BaseECU("ECU_B", 2, 0x200, master, tx_period=6.0, start_delay=2.0)
    ecu_c = BaseECU("ECU_C", 3, 0x300, master, tx_period=9.0, start_delay=2.0)
    ecu_d = BaseECU("ECU_D", 4, 0x400, master, tx_period=14.0, start_delay=2.0)

    ecus = [ecu_a, ecu_b, ecu_c, ecu_d]
    # Payload totalmente random per ogni ECU (richiesto)
    for ecu in ecus:
        ecu.random_payload = True

    # Create attacker (150s training + 30s reinforcement)
    attacker = WeepingAttacker(master, sniff_duration_1=150, sniff_duration_2=30)

    # Start all
    attacker.start()
    for ecu in ecus:
        ecu.start()

    print("\n=== Simulation running ===\n")

    victim_ecu = None

    try:
        while True:
            time.sleep(1)

            # Trova la vittima
            if attacker.victim_id and victim_ecu is None:
                for ecu in ecus:
                    if ecu.arb_id == attacker.victim_id:
                        victim_ecu = ecu
                        print(f"\n[MAIN] Victim identified: {victim_ecu.name} (ID={hex(victim_ecu.arb_id)})")
                        break

            # Check victim bus-off
            if victim_ecu and victim_ecu.is_bus_off():
                print(f"\n{'='*100}")
                print(f"🎉 ATTACK SUCCESSFUL! 🎉")
                print(f"Victim {victim_ecu.name} (ID={hex(victim_ecu.arb_id)}) is in BUS-OFF state")
                print(f"{'='*100}\n")
                break

            # Check attacker bus-off
            if attacker.is_bus_off():
                print(f"\n{'='*100}")
                print(f"❌ ATTACK FAILED! ❌")
                print(f"Attacker went BUS-OFF before victim")
                print(f"{'='*100}\n")
                break

    except KeyboardInterrupt:
        print("\n=== Simulation interrupted ===")

    # STAMPA FINALE TEC/REC
    print(f"\n{'='*100}")
    print("FINAL STATUS - TEC/REC of all ECUs")
    print(f"{'='*100}")

    for ecu in ecus:
        print(
            f"  [{ecu.name:8s}] ID=0x{ecu.arb_id:03X} | TEC={ecu.tec:3d} "
            f"REC={ecu.rec:3d} | {ecu.state.name:13s}"
        )

    print(
        f"  [{attacker.name:8s}] ID=0x{attacker.arb_id:03X} | TEC={attacker.tec:3d} "
        f"REC={attacker.rec:3d} | {attacker.state.name:13s}"
    )

    print(f"{'='*100}\n")

    # Stop all
    attacker.stop()
    for ecu in ecus:
        ecu.stop()
    master.stop()

    print("\n=== Simulation ended ===")


if __name__ == "__main__":
    main()
