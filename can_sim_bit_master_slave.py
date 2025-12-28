"""can_sim_bit_master_slave.py

Bit-level CAN (11-bit base frame) simulator with a *master* that mediates the bus.

Design goals (kept close to your existing script structure):
- ECUs are "slaves" that *provide the next bit* they intend to transmit.
- The master performs arbitration bit-by-bit, broadcasts the resolved bus bit to all slaves,
  and manages (simplified) TEC/REC updates + node states.
- When a full frame is transmitted successfully, the master can forward it to SocketCAN
  (default: vcan0).

IMPORTANT SAFETY NOTE
This is a teaching/test simulator. It includes a *fault injector* (e.g., flip r0) to test
error handling. It does NOT implement an automated bus-off attacker.
"""

from __future__ import annotations

import time
import threading
import queue
import random
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from typing import Deque, Dict, List, Optional, Tuple

try:
    import can  # python-can

    CAN_AVAILABLE = True
except Exception:
    CAN_AVAILABLE = False


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


class MasterState(Enum):
    IDLE = auto()
    START_SLOT = auto()
    ARBITRATION = auto()
    TRANSMIT = auto()
    ERROR_FLAG = auto()
    EOF = auto()
    INTERFRAME = auto()


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
class TransmissionRequest:
    slave_name: str
    slave_id: int
    arbitration_id: int
    data: bytes
    timestamp: float


@dataclass
class BitTransmission:
    bit_value: BitValue
    timestamp: float
    sender_name: str
    field: Field


def _crc15_can(bits: List[int]) -> int:
    """Compute CRC-15/CAN over a bit stream.

    Polynomial: x^15 + x^14 + x^10 + x^8 + x^7 + x^4 + x^3 + 1
    Poly (without x^15): 0x4599.
    Init: 0.

    NOTE: This is *good enough* for simulation; you can swap with the exact variant
    used in your slides if needed.
    """

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
        push(BitValue.DOMINANT, Field.RTR)  # Data frame
        push(BitValue.DOMINANT, Field.IDE)  # Base (11-bit)
        push(self.r0, Field.R0)             # r0 (normally recessive)

        # DLC 4 bits
        dlc = len(self.data)
        for i in range(3, -1, -1):
            push(BitValue.from_int((dlc >> i) & 1), Field.DLC)

        # DATA bytes
        for byte in self.data:
            for i in range(7, -1, -1):
                push(BitValue.from_int((byte >> i) & 1), Field.DATA)

        # CRC over *destuffed* bits from SOF to end of data
        crc_input = [int(b) for b in bits]  # 0/1
        crc = _crc15_can(crc_input)
        for i in range(14, -1, -1):
            push(BitValue.from_int((crc >> i) & 1), Field.CRC)

        # CRC delimiter (recessive)
        push(BitValue.RECESSIVE, Field.CRC_DELIM)
        # ACK slot (recessive; receivers may drive dominant). We keep it recessive here.
        push(BitValue.RECESSIVE, Field.ACK_SLOT)
        push(BitValue.RECESSIVE, Field.ACK_DELIM)
        # EOF 7 recessive
        for _ in range(7):
            push(BitValue.RECESSIVE, Field.EOF)
        # Intermission 3 recessive (separate from EOF so master can model bus idle)
        for _ in range(3):
            push(BitValue.RECESSIVE, Field.INTERMISSION)

        return bits, fields

    @staticmethod
    def _apply_bit_stuffing(bits: List[BitValue], fields: List[Field]) -> Tuple[List[BitValue], List[Field]]:
        """Stuff from SOF through end of CRC sequence (inclusive).

        We assume fields identify CRC bits as Field.CRC.
        Stuff rule: after 5 consecutive equal bits, insert complement bit.
        """

        out_bits: List[BitValue] = []
        out_fields: List[Field] = []

        run_val: Optional[BitValue] = None
        run_len = 0

        def should_stuff(idx: int) -> bool:
            # Stuff from SOF up to and including CRC sequence.
            return fields[idx] in {
                Field.SOF, Field.ID, Field.RTR, Field.IDE, Field.R0, Field.DLC, Field.DATA, Field.CRC
            }

        for i, (b, f) in enumerate(zip(bits, fields)):
            out_bits.append(b)
            out_fields.append(f)

            if not should_stuff(i):
                # Reset stuff tracking after CRC sequence.
                run_val = None
                run_len = 0
                continue

            if run_val is None or b != run_val:
                run_val = b
                run_len = 1
            else:
                run_len += 1

            if run_len == 5:
                stuffed = BitValue.DOMINANT if b is BitValue.RECESSIVE else BitValue.RECESSIVE
                out_bits.append(stuffed)
                out_fields.append(Field.STUFF)
                run_val = None
                run_len = 0

        return out_bits, out_fields

    def _build(self):
        raw_bits, raw_fields = self._build_unstuffed_payload_bits()
        stuffed_bits, stuffed_fields = self._apply_bit_stuffing(raw_bits, raw_fields)
        self.bits = stuffed_bits
        self.fields = stuffed_fields


class FaultInjector:
    """Optional: inject deterministic faults for testing.

    Example: force R0 to DOMINANT once every N frames (simulates a faulty transceiver/noise).
    """

    def __init__(self, *, flip_r0_every_n_frames: int = 0):
        self.flip_r0_every_n_frames = flip_r0_every_n_frames
        self._frame_count = 0

    def on_new_frame(self):
        self._frame_count += 1

    def override_bus_bit(self, field: Field, current_bus: BitValue) -> BitValue:
        if self.flip_r0_every_n_frames and field == Field.R0:
            if (self._frame_count % self.flip_r0_every_n_frames) == 0:
                # Force dominant on the bus during r0
                return BitValue.DOMINANT
        return current_bus


class BaseECU:
    def __init__(
        self,
        name: str,
        slave_id: int,
        arb_id: int,
        master: "CANMaster",
        period: float = 2.0,
        start_delay: float = 0.0,
        auto_tx: bool = True,
    ):
        self.name = name
        self.slave_id = slave_id
        self.arb_id = arb_id & 0x7FF
        self.master = master

        self.period = period
        self.start_delay = start_delay

        self.tec = 0
        self.rec = 0
        self.state = NodeState.ERROR_ACTIVE

        self._stop = False
        self.auto_tx = bool(auto_tx)
        self._tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

        # Transmission state
        self._pending_req: Optional[TransmissionRequest] = None
        self._bitstream: Optional[CANBitStream] = None
        self._cursor = 0
        self._currently_transmitting = False

        self.master.register_slave(self)

    def start(self):
        print(f"[{self.name}] START slave_id={self.slave_id} ID=0x{self.arb_id:03X}")
        self._rx_thread.start()
        if self.auto_tx:
            self._tx_thread.start()

    def request_once(self, data: bytes, *, arbitration_id: Optional[int] = None):
        """Queue exactly one transmission (used for deterministic tests).

        If arbitration_id is None, uses this ECU's configured arb_id.
        """
        if self.is_bus_off():
            print(f"[{self.name}] request_once ignored (BUS_OFF)")
            return
        if self._pending_req is not None:
            print(f"[{self.name}] request_once ignored (already pending)")
            return
        now = time.time()
        aid = self.arb_id if arbitration_id is None else (arbitration_id & 0x7FF)
        self._pending_req = TransmissionRequest(
            slave_name=self.name,
            slave_id=self.slave_id,
            arbitration_id=aid,
            data=data[:8],
            timestamp=now,
        )
        self._bitstream = None
        self._cursor = 0
        self.master.submit_request(self._pending_req)
        print(f"[{self.name}] request_once queued (ID=0x{aid:03X})")

    def stop(self):
        self._stop = True
        print(f"[{self.name}] STOP TEC={self.tec} REC={self.rec} state={self.state.name}")

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
        elif self.tec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    # -------- Master-facing API --------

    def is_bus_off(self) -> bool:
        return self.state is NodeState.BUS_OFF

    def has_pending_frame(self) -> bool:
        return (self._pending_req is not None) and (self._bitstream is not None) and (not self.is_bus_off())

    def begin_frame_if_needed(self):
        """Ensure bitstream is ready for a pending request."""
        if self._pending_req is None or self._bitstream is not None:
            return
        # r0 normally recessive
        self._bitstream = CANBitStream(self._pending_req.arbitration_id, self._pending_req.data, r0=BitValue.RECESSIVE)
        self._cursor = 0

    def peek_next_bit(self) -> Optional[Tuple[BitValue, Field]]:
        if not self.has_pending_frame():
            return None
        assert self._bitstream is not None
        if self._cursor >= len(self._bitstream.bits):
            return None
        return self._bitstream.bits[self._cursor], self._bitstream.fields[self._cursor]

    def advance(self):
        self._cursor += 1

    def reset_for_retransmission(self):
        self._cursor = 0
        self._currently_transmitting = False

    def mark_as_transmitting(self, value: bool):
        self._currently_transmitting = value

    def on_bus_bit(self, bus_bit: BitValue, field: Field, *, arbitration_window: bool):
        """Bit monitoring for the *current transmitter*.

        - During arbitration window (SOF/ID/RTR), a recessive overwritten by dominant means losing arbitration (not error).
        - Outside arbitration: recessive overwritten by dominant => BIT ERROR.
        """
        if not self._currently_transmitting:
            return
        nxt = self.peek_next_bit()
        if nxt is None:
            return
        sent_bit, _sent_field = nxt
        if sent_bit is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
            if arbitration_window:
                # losing arbitration is handled by master; do nothing here.
                return
            # Bit error
            self.master.report_bit_error(self.slave_id, offender="bit_monitoring")

    def apply_error_update(self, *, tec_delta: int = 0, rec_delta: int = 0):
        self.tec = max(0, self.tec + tec_delta)
        self.rec = max(0, self.rec + rec_delta)
        self._update_state()

    def apply_success_update(self):
        # Simplified: successful TX decrements TEC by 1.
        self.tec = max(0, self.tec - 1)
        self._update_state()

    # -------- Internal threads --------

    def _tx_loop(self):
        if not self.auto_tx:
            return
        time.sleep(self.start_delay)
        # First transmission happens immediately after start_delay.
        next_tx = time.time()
        while not self._stop:
            if self.is_bus_off():
                time.sleep(0.2)
                continue
            now = time.time()
            if now >= next_tx:
                # Create a new pending request only if none is pending.
                if self._pending_req is None:
                    data = bytes(random.randint(0, 255) for _ in range(8))
                    self._pending_req = TransmissionRequest(
                        slave_name=self.name,
                        slave_id=self.slave_id,
                        arbitration_id=self.arb_id,
                        data=data,
                        timestamp=now,
                    )
                    self._bitstream = None
                    self._cursor = 0
                    self.master.submit_request(self._pending_req)
                    print(f"[{self.name}] TX request queued (ID=0x{self.arb_id:03X}) TEC={self.tec} state={self.state.name}")
                next_tx = now + self.period
            time.sleep(0.01)

    def _rx_loop(self):
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, timeout=0.1)
            if bt is None:
                continue
            # Slaves can inspect bt for debugging; keep light.
            # (You can add per-ECU prints here if you want.)
            pass


class CANMaster:
    def __init__(
        self,
        tick_ms: float = 0.1,
        start_slot_ticks: int = 50,
        forward_to_socketcan: bool = False,
        can_channel: str = "vcan0",
        fault_injector: Optional[FaultInjector] = None,
    ):
        self.tick = tick_ms / 1000.0
        self.state = MasterState.IDLE
        self.clock = 0

        self.slaves: Dict[int, BaseECU] = {}
        self.bit_queues: Dict[int, "queue.Queue[BitTransmission]"] = {}
        self._pending_starts: "queue.Queue[TransmissionRequest]" = queue.Queue()

        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)

        # Bus activity
        self._contenders: List[int] = []
        self._active_senders: List[int] = []
        self._winner: Optional[int] = None
        self._current_field: Field = Field.INTERMISSION
        self._arbitration_window = False
        self._error_sender: Optional[int] = None
        self._error_flag_bits_left = 0
        self._frame_ok = True

        # "Start slot" to make arbitration deterministic in a discrete-time simulator.
        # When the bus is idle and at least one ECU asks to transmit, we keep the bus in
        # START_SLOT for N ticks to collect other near-simultaneous requests, then begin
        # arbitration with the full set.
        self.start_slot_ticks = max(1, int(start_slot_ticks))
        self._start_slot_left = 0
        self._start_slot_contenders: List[int] = []

        self._fault = fault_injector or FaultInjector()

        # SocketCAN (safe default: disabled)
        self.forward = bool(forward_to_socketcan and CAN_AVAILABLE)
        self.hw_bus = None
        self.can_channel = can_channel
        if self.forward:
            # For safety, default to vcan*; you can change explicitly.
            try:
                self.hw_bus = can.interface.Bus(channel=can_channel, interface="socketcan")
                print(f"[MASTER] SocketCAN enabled on {can_channel}")
            except Exception as e:
                print(f"[MASTER] SocketCAN init failed: {e}")
                self.forward = False

    def register_slave(self, ecu: BaseECU):
        self.slaves[ecu.slave_id] = ecu
        self.bit_queues[ecu.slave_id] = queue.Queue()
        print(f"[MASTER] Registered ECU {ecu.name} (slave_id={ecu.slave_id}, ID=0x{ecu.arb_id:03X})")

    def submit_request(self, req: TransmissionRequest):
        # Just a "start intent"; the ECU will actually provide bits.
        print(f"[MASTER] RX start-intent from {req.slave_name} (ID=0x{req.arbitration_id:03X})")
        self._pending_starts.put(req)

    def get_bit_for_slave(self, slave_id: int, timeout: float = 0.01) -> Optional[BitTransmission]:
        q = self.bit_queues.get(slave_id)
        if q is None:
            return None
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    def start(self):
        print("[MASTER] START")
        self._thread.start()

    def stop(self):
        self._stop = True
        self._thread.join(timeout=2)
        if self.hw_bus:
            try:
                self.hw_bus.shutdown()
            except Exception:
                pass
        print("[MASTER] STOP")

    # -------- Error reporting --------

    def report_bit_error(self, sender_slave_id: int, offender: str = "unknown"):
        # Only first error wins for this frame.
        if self.state in {MasterState.ERROR_FLAG, MasterState.EOF, MasterState.INTERFRAME}:
            return
        self._frame_ok = False
        self._error_sender = sender_slave_id
        sender = self.slaves.get(sender_slave_id)
        if sender is None:
            return
        print(f"[MASTER] ERROR: bit error reported by {sender.name} (state={sender.state.name}, offender={offender})")
        self.state = MasterState.ERROR_FLAG
        self._error_flag_bits_left = 6

        # TEC update for sender
        self._apply_error_counters(sender_slave_id)
        # Abort: all contenders/sender stop transmitting now.
        for sid in set(list(self._contenders) + list(self._active_senders)):
            if sid in self.slaves:
                self.slaves[sid].mark_as_transmitting(False)

    def _apply_error_counters(self, sender_slave_id: int):
        sender = self.slaves[sender_slave_id]
        sender.apply_error_update(tec_delta=8)
        # As you requested: if ERROR ACTIVE, others REC += 1.
        if sender.state is NodeState.ERROR_ACTIVE:
            for sid, ecu in self.slaves.items():
                if sid != sender_slave_id and not ecu.is_bus_off():
                    ecu.apply_error_update(rec_delta=1)
        print(f"[MASTER] Counter update: {sender.name}.TEC={sender.tec} state={sender.state.name}")

    # -------- Main loop --------

    def _loop(self):
        while not self._stop:
            self.clock += 1
            if self.state == MasterState.IDLE:
                self._handle_idle()
            elif self.state == MasterState.START_SLOT:
                self._handle_start_slot()
            elif self.state == MasterState.ARBITRATION:
                self._handle_arbitration_step()
            elif self.state == MasterState.TRANSMIT:
                self._handle_transmit_step()
            elif self.state == MasterState.ERROR_FLAG:
                self._handle_error_flag_step()
            elif self.state == MasterState.EOF:
                self._handle_eof()
            elif self.state == MasterState.INTERFRAME:
                self._handle_interframe()

            time.sleep(self.tick)

    def _drain_start_intents(self) -> List[int]:
        """Collect start intents; returns list of slave_ids to contend next."""
        new_contenders: List[int] = []
        while True:
            try:
                req = self._pending_starts.get_nowait()
            except queue.Empty:
                break
            ecu = self.slaves.get(req.slave_id)
            if ecu is None or ecu.is_bus_off():
                continue
            # Ensure ECU knows about the pending request
            ecu._pending_req = req
            ecu._bitstream = None
            ecu._cursor = 0
            ecu.begin_frame_if_needed()
            if ecu.has_pending_frame() and req.slave_id not in new_contenders:
                new_contenders.append(req.slave_id)
        return new_contenders

    def _broadcast(self, bus_bit: BitValue, sender_name: str, field: Field):
        bt = BitTransmission(bus_bit, time.time(), sender_name, field)
        for q in self.bit_queues.values():
            try:
                q.put_nowait(bt)
            except Exception:
                pass

    def _handle_idle(self):
        contenders = self._drain_start_intents()
        if not contenders:
            return

        # Start-slot: collect near-simultaneous requests deterministically.
        self._start_slot_contenders = list(dict.fromkeys(contenders))
        self._start_slot_left = self.start_slot_ticks
        self._winner = None
        self._active_senders = []
        self._frame_ok = True
        self._error_sender = None
        self._fault.on_new_frame()
        print(
            f"[MASTER] IDLE→START_SLOT ({self._start_slot_left} ticks) initial="
            f"{','.join(self.slaves[s].name for s in self._start_slot_contenders)}"
        )
        self.state = MasterState.START_SLOT

    def _handle_start_slot(self):
        more = self._drain_start_intents()
        for sid in more:
            if sid not in self._start_slot_contenders:
                self._start_slot_contenders.append(sid)

        self._start_slot_left -= 1
        if self._start_slot_left > 0:
            return

        self._contenders = list(self._start_slot_contenders)
        self._start_slot_contenders = []
        for sid in self._contenders:
            self.slaves[sid].begin_frame_if_needed()
            self.slaves[sid].reset_for_retransmission()

        print(f"[MASTER] START_SLOT→ARBITRATION contenders={','.join(self.slaves[s].name for s in self._contenders)}")
        self.state = MasterState.ARBITRATION

    def _get_arbitration_bit(self, ecu: BaseECU) -> Optional[Tuple[BitValue, Field]]:
        nxt = ecu.peek_next_bit()
        if nxt is None:
            return None
        bit, field = nxt
        return bit, field

    def _handle_arbitration_step(self):
        # Arbitration window includes SOF, ID, RTR.
        self._arbitration_window = True

        # Ask contenders their next bit.
        offered: List[Tuple[int, BitValue, Field]] = []
        for sid in list(self._contenders):
            ecu = self.slaves[sid]
            if ecu.is_bus_off() or not ecu.has_pending_frame():
                self._contenders.remove(sid)
                continue
            nxt = self._get_arbitration_bit(ecu)
            if nxt is None:
                self._contenders.remove(sid)
                continue
            b, f = nxt
            offered.append((sid, b, f))

        if not offered:
            print("[MASTER] ARBITRATION: no offered bits -> back to IDLE")
            self.state = MasterState.IDLE
            return

        # Determine bus bit.
        bus_bit = BitValue.DOMINANT if any(b is BitValue.DOMINANT for _, b, _ in offered) else BitValue.RECESSIVE
        # Use the first offered field as "current" field (they're aligned in a real bus).
        self._current_field = offered[0][2]
        bus_bit = self._fault.override_bus_bit(self._current_field, bus_bit)

        # Print master decision.
        s = ", ".join(f"{self.slaves[sid].name}:{b.name}" for sid, b, _ in offered)
        print(f"[MASTER] ARB bit: field={self._current_field.name} | {s} -> BUS={bus_bit.name}")

        # Broadcast resolved bus bit.
        self._broadcast(bus_bit, sender_name="BUS", field=self._current_field)

        # Arbitration: contenders sending recessive while bus dominant lose (only in ID/RTR).
        if self._current_field in {Field.ID, Field.RTR}:
            losers: List[int] = []
            for sid, b, _f in offered:
                if b is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
                    losers.append(sid)
            for sid in losers:
                ecu = self.slaves[sid]
                print(f"[MASTER] ARB: {ecu.name} loses arbitration -> waits for next bus idle")
                ecu.reset_for_retransmission()
                self._contenders.remove(sid)

        # Advance cursor for those still contending (they actually sent this bit).
        for sid, _b, _f in offered:
            if sid in self._contenders:
                self.slaves[sid].advance()

        # If exactly one remains -> clear winner.
        if len(self._contenders) == 1:
            self._winner = self._contenders[0]
            self._active_senders = [self._winner]
            win_ecu = self.slaves[self._winner]
            win_ecu.mark_as_transmitting(True)
            print(f"[MASTER] ARBITRATION DONE -> winner={win_ecu.name}, switching to TRANSMIT")
            self.state = MasterState.TRANSMIT
            return

        # If we just transmitted RTR and more than one contender still matches, arbitration is over
        # (same ID+RTR). From now on, multiple senders may transmit in lockstep.
        if self._current_field == Field.RTR and len(self._contenders) > 1:
            self._active_senders = list(self._contenders)
            self._winner = self._active_senders[0]
            for sid in self._active_senders:
                self.slaves[sid].mark_as_transmitting(True)
            names = ",".join(self.slaves[s].name for s in self._active_senders)
            print(f"[MASTER] ARBITRATION TIE (same ID/RTR) -> active_senders={names}, switching to TRANSMIT")
            self.state = MasterState.TRANSMIT

    def _handle_transmit_step(self):
        assert self._winner is not None

        # While bus is busy, new start intents are queued and will be served later.
        _ = self._drain_start_intents()

        if not self._active_senders:
            self._active_senders = [self._winner]

        # Collect next bit from every active sender (lockstep).
        offered: List[Tuple[int, BitValue, Field]] = []
        for sid in list(self._active_senders):
            ecu = self.slaves[sid]
            nxt = ecu.peek_next_bit()
            if nxt is None:
                continue
            b, f = nxt
            offered.append((sid, b, f))

        if not offered:
            # All senders ended.
            for sid in self._active_senders:
                self.slaves[sid].mark_as_transmitting(False)
            self.state = MasterState.EOF
            return

        # Resolve bus bit.
        field = offered[0][2]
        if any(f != field for _sid, _b, f in offered):
            # Shouldn't happen if lockstep is correct; keep sim running.
            field = Field.STUFF
        self._current_field = field
        self._arbitration_window = field in {Field.SOF, Field.ID, Field.RTR}

        bus_bit = BitValue.DOMINANT if any(b is BitValue.DOMINANT for _sid, b, _f in offered) else BitValue.RECESSIVE
        bus_bit = self._fault.override_bus_bit(field, bus_bit)

        s = ", ".join(f"{self.slaves[sid].name}:{b.name}" for sid, b, _ in offered)
        print(f"[MASTER] TX bit: field={field.name} | {s} -> BUS={bus_bit.name}")

        # Broadcast resolved bus bit once.
        self._broadcast(bus_bit, sender_name="BUS", field=field)

        # Bit monitoring for each sender.
        for sid, _b, _f in offered:
            self.slaves[sid].on_bus_bit(bus_bit, field, arbitration_window=self._arbitration_window)

        # Advance all only if no error state transition happened.
        if self.state == MasterState.TRANSMIT:
            for sid, _b, _f in offered:
                self.slaves[sid].advance()

    def _handle_error_flag_step(self):
        # Master puts error flag bits on bus, based on sender's state.
        if self._error_sender is None:
            self.state = MasterState.INTERFRAME
            return
        sender = self.slaves[self._error_sender]
        flag_bit = BitValue.DOMINANT if sender.state is NodeState.ERROR_ACTIVE else BitValue.RECESSIVE
        self._current_field = Field.STUFF  # generic
        print(f"[MASTER] ERROR_FLAG ({sender.state.name}): BUS={flag_bit.name} ({self._error_flag_bits_left} bits left)")
        self._broadcast(flag_bit, sender_name="ERROR", field=Field.STUFF)
        self._error_flag_bits_left -= 1
        if self._error_flag_bits_left <= 0:
            # Abort frame and go to EOF handling (for SocketCAN forwarding decision)
            self.state = MasterState.EOF

    def _handle_eof(self):
        # Decide what to forward.
        if self._frame_ok and self._winner is not None:
            # Forward exactly once (bus has one frame), but apply success update to all senders
            # that participated in the transmission.
            sender0 = self.slaves[self._winner]
            req0 = sender0._pending_req
            if req0 is not None:
                print(f"[MASTER] EOF: frame OK -> forward DATA id=0x{req0.arbitration_id:03X} data={req0.data.hex().upper()}")
                for sid in (self._active_senders or [self._winner]):
                    ecu = self.slaves[sid]
                    ecu.apply_success_update()
                    ecu._pending_req = None
                    ecu._bitstream = None
                    ecu._cursor = 0
                if self.forward and self.hw_bus:
                    try:
                        msg = can.Message(arbitration_id=req0.arbitration_id, data=req0.data, is_extended_id=False)
                        self.hw_bus.send(msg)
                    except Exception as e:
                        print(f"[MASTER] SocketCAN send failed: {e}")
        else:
            # Error frame only
            if self._error_sender is not None:
                sender = self.slaves[self._error_sender]
                print(f"[MASTER] EOF: error -> forward ERROR ({sender.state.name}) only")
                if self.forward and self.hw_bus:
                    try:
                        # Best-effort error frame (socketcan supports it; may require special permissions).
                        msg = can.Message(arbitration_id=0, data=b"", is_error_frame=True)
                        self.hw_bus.send(msg)
                    except Exception as e:
                        print(f"[MASTER] SocketCAN error-frame send failed: {e}")

            # Retransmission: winner keeps pending req; reset cursor.
            if self._winner is not None:
                self.slaves[self._winner].reset_for_retransmission()

        self.state = MasterState.INTERFRAME

    def _handle_interframe(self):
        # One tick of interframe is enough for our discrete sim.
        print("[MASTER] INTERFRAME -> IDLE")
        self._contenders = []
        self._active_senders = []
        self._winner = None
        self._error_sender = None
        self._frame_ok = True
        self.state = MasterState.IDLE


def main():
    print("CAN master-slave bit-level simulator (continuous bus-off test)")

    # IMPORTANT: default fault injection is OFF.
    # (If you enable flip_r0_every_n_frames, a node can "go in error da sola")
    fault = FaultInjector(flip_r0_every_n_frames=0)

    master = CANMaster(
        tick_ms=0.5,
        start_slot_ticks=200,
        forward_to_socketcan=False,  # keep safe by default
        can_channel="vcan0",
        fault_injector=None,
    )
    master.start()

    # ------------------------------------------------------------
    # 4 ECU sempre attive - continuano a trasmettere fino a BUS-OFF
    # ------------------------------------------------------------
    ecu_a = BaseECU("ECU_A", 1, 0x100, master, auto_tx=False)
    ecu_b = BaseECU("ECU_B", 2, 0x080, master, auto_tx=False)
    ecu_d = BaseECU("ECU_D", 4, 0x123, master, auto_tx=False)
    ecu_e = BaseECU("ECU_E", 5, 0x123, master, auto_tx=False)

    ecu_a.start()
    ecu_b.start()
    ecu_d.start()
    ecu_e.start()

    print("Simulazione avviata - continua fino a BUS-OFF... (Ctrl+C per fermare)")

    try:
        cycle = 0
        while True:
            cycle += 1
            
            # TEST 1: Arbitration (different IDs)
            ecu_a.request_once(b"\x11\x11\x11\x11\x11\x11\x11\x11")
            ecu_b.request_once(b"\x22\x22\x22\x22\x22\x22\x22\x22")
            
            # TEST 2: Collision (same ID, different data) → genera errori!
            ecu_d.request_once(b"\xAA\x00\x00\x00\x00\x00\x00\x00")
            ecu_e.request_once(b"\xAB\x00\x00\x00\x00\x00\x00\x00")
            
            # Status ogni 10 cicli
            if cycle % 10 == 0:
                print(f"\n[CYCLE {cycle}] "
                      f"A:TEC={ecu_a.tec}({ecu_a.state.name}) "
                      f"B:TEC={ecu_b.tec}({ecu_b.state.name}) "
                      f"D:TEC={ecu_d.tec}({ecu_d.state.name}) "
                      f"E:TEC={ecu_e.tec}({ecu_e.state.name})")
            
            # Check BUS-OFF → ferma se una ECU è in BUS-OFF
            if (ecu_a.isbusoff() or ecu_b.isbusoff() or 
                ecu_d.isbusoff() or ecu_e.isbusoff()):
                print(f"\n*** BUS-OFF rilevato dopo {cycle} cicli! ***")
                print(f"A:TEC={ecu_a.tec}({ecu_a.state.name}) "
                      f"B:TEC={ecu_b.tec}({ecu_b.state.name}) "
                      f"D:TEC={ecu_d.tec}({ecu_d.state.name}) "
                      f"E:TEC={ecu_e.tec}({ecu_e.state.name})")
                break
                
            time.sleep(3)  # Tempo per trasmissioni + error handling
            
    except KeyboardInterrupt:
        print("\nInterrotto manualmente")

    # Cleanup finale
    print("\n[FINAL STATUS]")
    print(f"A:TEC={ecu_a.tec}({ecu_a.state.name}) "
          f"B:TEC={ecu_b.tec}({ecu_b.state.name}) "
          f"D:TEC={ecu_d.tec}({ecu_d.state.name}) "
          f"E:TEC={ecu_e.tec}({ecu_e.state.name})")

    ecu_a.stop(); ecu_b.stop(); ecu_d.stop(); ecu_e.stop()
    master.stop()



if __name__ == "__main__":
    main()
