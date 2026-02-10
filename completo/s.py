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


# --- CAN BUS MASTER ---
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
        with self.lock:
            self.ecus[ecu.name] = ecu

    def submit_frame(self, ecu, data: bytes, arb_id: int, r0: BitValue):
        with self.lock:
            self.pending.append((ecu, data, arb_id & 0x7FF, r0))

    def start(self):
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop = True

    def _loop(self):
        while not self._stop:
            time.sleep(self.collect_window)
            with self.lock:
                if not self.pending:
                    continue
                contenders = self.pending[:]
                self.pending.clear()

            self._process_contenders(contenders)

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

    # =========================
    #  SOLO QUESTA FUNZIONE È STATA MODIFICATA
    # =========================
    def _handle_collision(self, bitstreams, active, start_bit_idx):
        """Gestisce collisione tra ECU con stesso ID (bit monitoring -> error flag)."""
        bit_idx = start_bit_idx
        error_detected = False
        offender_ecu = None
        offender_idx = None
        winner_idx = None  # chi continua a trasmettere se l'error-flag è PASSIVE

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
            if field not in {Field.SOF, Field.ID, Field.RTR}:
                for i, ecu, bit, _ in offered:
                    if bit is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
                        print(f"[MASTER] BIT ERROR rilevato da {ecu.name} (offender=bit_monitoring) -> error flag, frame abortito")
                        error_detected = True
                        offender_ecu = ecu
                        offender_idx = i
                        # Chi ha messo DOMINANT su quel bit è quello che continua se l'offender è ERROR_PASSIVE
                        for j, ecu2, bit2, _ in offered:
                            if bit2 is BitValue.DOMINANT:
                                winner_idx = j
                                break
                        break

            bit_idx += 1

        if error_detected and offender_ecu:
            self._send_error_flag(offender_ecu)

            involved = [bitstreams[i][0] for i in active]

            # --- Gestione TEC coerente con i tuoi scenari ---
            if offender_ecu.state is NodeState.ERROR_ACTIVE:
                # Error Flag ACTIVE domina sul bus -> la trasmissione si interrompe per tutti i contendenti
                # Scenario 1 e Scenario 2.2: tutte le ECU coinvolte nella collisione TEC +8
                for i in active:
                    ecu = bitstreams[i][0]
                    ecu.tec += 8
                    ecu._update_state()
                    print(f"[MASTER] {ecu.name}: TEC={ecu.tec} (+8 per errore ACTIVE) State={ecu.state.name}")

                # Listener REC +1
                for ecu in self.ecus.values():
                    if ecu not in involved and not ecu.is_bus_off():
                        ecu.rec += 1
                        print(f"[MASTER] {ecu.name}: REC={ecu.rec} (+1 per errore ricevuto)")

                return None, None, None, None

            else:
                # offender in ERROR_PASSIVE -> invia Error Flag PASSIVE (recessivo) e viene sovrascritto
                # chi "vince" su quel bit continua e potrà ottenere TEC -1 a fine frame
                offender_ecu.tec += 7
                offender_ecu._update_state()
                print(f"[MASTER] {offender_ecu.name}: TEC={offender_ecu.tec} (+7 per errore PASSIVE) State={offender_ecu.state.name}")

                # Listener REC +1 (mantengo il modello esistente)
                for ecu in self.ecus.values():
                    if ecu not in involved and not ecu.is_bus_off():
                        ecu.rec += 1
                        print(f"[MASTER] {ecu.name}: REC={ecu.rec} (+1 per errore ricevuto)")

                if winner_idx is not None:
                    w_ecu, _, w_id, w_data, w_r0 = bitstreams[winner_idx]
                    print(f"[MASTER] CONTINUE TX: {w_ecu.name} (ID=0x{w_id:03X})")
                    return w_ecu, w_data, w_id, w_r0

        return None, None, None, None

    def _send_error_flag(self, offender_ecu):
        """Invia error flag coerente con lo stato dell'offender."""
        if offender_ecu.state is NodeState.ERROR_PASSIVE:
            self._send_error_flag_passive(offender_ecu)
        else:
            self._send_error_flag_active(offender_ecu)

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
        """Invia error flag passive (6 bit recessivi)"""
        print(f"\n[MASTER] Sending ERROR FLAG PASSIVE (6 recessive bits)")

        for bit_num in range(6):
            print(f"  [ERR] ERROR_FLAG_PASSIVE | {offender_ecu.name} -> BUS=1 (bit {bit_num+1}/6)")

        # su vcan0 non mando nulla (non domina il bus), mantenuto com'era

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

        self.state = NodeState.ERROR_ACTIVE
        self.tec = 0
        self.rec = 0

        self._stop = False
        self._tx_thread = None
        self.next_tx_time = time.time() + self.start_delay

    def start(self):
        print(f"[{self.name}] ECU started (ID=0x{self.arb_id:03X})")
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

    def _tx_loop(self):
        while not self._stop:
            now = time.time()
            if now < self.next_tx_time:
                time.sleep(min(0.01, self.next_tx_time - now))
                continue

            data = self._create_message()
            self.master.submit_frame(self, data, self.arb_id, BitValue.RECESSIVE)

            self.next_tx_time = time.time() + self.tx_period

    def _create_message(self) -> bytes:
        return bytes([self.slave_id & 0xFF] + [0x00] * 7)


# --- Victim ECU ---
class VictimECU(BaseECU):
    pass


# --- Attacker ECU ---
class AttackerECU(BaseECU):
    def __init__(self, name: str, slave_id: int, arb_id: int, master: CANBusMaster,
                 tx_period: float = 3.0, start_delay: float = 0.0):
        super().__init__(name, slave_id, arb_id, master, tx_period, start_delay)

        self.enabled = True
        self.model = MultiOutputClassifier(RandomForestClassifier(n_estimators=50, random_state=42))
        self.trained = False
        self.buffer_bits = []
        self.target_prob_zero = None

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def observe_bits(self, bits: List[int]):
        self.buffer_bits.append(bits)
        if len(self.buffer_bits) > 1000:
            self.buffer_bits.pop(0)

    def train(self):
        if len(self.buffer_bits) < 50:
            return
        X = np.array([b[:-1] for b in self.buffer_bits])
        Y = np.array([b[1:] for b in self.buffer_bits])
        self.model.fit(X, Y)
        self.trained = True

    def predict_next_bit_prob(self, context: List[int]) -> float:
        if not self.trained:
            return 0.5
        proba = self.model.predict_proba([context])
        # proba is list of (n_outputs) arrays [ [P(0), P(1)] ]
        # we want P(next_bit=0) for the first predicted output
        return float(proba[0][0][0])

    def _create_message(self) -> bytes:
        if not self.enabled:
            return super()._create_message()

        payload = self._create_attack_message()
        return payload

    def _create_attack_message(self) -> bytes:
        """Crea il payload dell'attacco (dato CAN)."""
        # Qui non tocco nulla (come richiesto): uso quello che avevi già implementato
        # e/o quello che mi avevi dato in precedenza nel file.
        return bytes([self.slave_id & 0xFF] + [0xFF] * 7)


# --- Example runner ---
if __name__ == "__main__":
    master = CANBusMaster(use_vcan=False)

    victim = VictimECU("victim", slave_id=0xD1, arb_id=0x100, master=master, tx_period=0.5)
    attacker = AttackerECU("attacker", slave_id=0xA1, arb_id=0x100, master=master, tx_period=0.5, start_delay=0.0)

    master.register_ecu(victim)
    master.register_ecu(attacker)

    master.start()
    victim.start()
    attacker.start()

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        victim.stop()
        attacker.stop()
        master.stop()