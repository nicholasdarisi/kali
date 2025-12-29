"""can_sim_dynamic.py

Simulatore CAN dinamico con timer individuali per ogni ECU.
Le ECU con ID minore (priorità alta) hanno tempi di attesa maggiori.
Le ECU con ID maggiore (priorità bassa) hanno tempi di attesa minori.

CORREZIONI IMPLEMENTATE:
1. START_SLOT eliminato: tutte le ECU PENDING partecipano IMMEDIATAMENTE all'arbitraggio
2. ERROR FLAG ACTIVE: 6 bit DOMINANT (0) quando TEC < 128
3. ERROR FLAG PASSIVE: 8 bit RECESSIVE (1) quando TEC >= 128
4. TEC decrementato (-1) dopo trasmissione con successo
5. Collision: ENTRAMBE le ECU incrementano TEC di +8
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
    ARBITRATION = auto()
    TRANSMIT = auto()
    ERROR_FLAG = auto()
    ERROR_DELIM = auto()
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
    def _apply_bit_stuffing(bits: List[BitValue], fields: List[Field]) -> Tuple[List[BitValue], List[Field]]:
        """Stuff from SOF through end of CRC sequence (inclusive)."""
        out_bits: List[BitValue] = []
        out_fields: List[Field] = []

        run_val: Optional[BitValue] = None
        run_len = 0

        def should_stuff(idx: int) -> bool:
            return fields[idx] in {
                Field.SOF, Field.ID, Field.RTR, Field.IDE, Field.R0, Field.DLC, Field.DATA, Field.CRC
            }

        for i, (b, f) in enumerate(zip(bits, fields)):
            out_bits.append(b)
            out_fields.append(f)

            if not should_stuff(i):
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
    """Optional: inject deterministic faults for testing."""

    def __init__(self, *, flip_r0_every_n_frames: int = 0):
        self.flip_r0_every_n_frames = flip_r0_every_n_frames
        self._frame_count = 0

    def on_new_frame(self):
        self._frame_count += 1

    def override_bus_bit(self, field: Field, current_bus: BitValue) -> BitValue:
        if self.flip_r0_every_n_frames and field == Field.R0:
            if (self._frame_count % self.flip_r0_every_n_frames) == 0:
                return BitValue.DOMINANT
        return current_bus


class BaseECU:
    def __init__(
        self,
        name: str,
        slave_id: int,
        arb_id: int,
        master: "CANMaster",
        tx_period: float = 2.0,
        start_delay: float = 0.0,
        auto_tx: bool = True,
    ):
        self.name = name
        self.slave_id = slave_id
        self.arb_id = arb_id & 0x7FF
        self.master = master

        self.tx_period = tx_period
        self.start_delay = start_delay
        self.next_tx_time = 0.0

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

        self._silence_bit_errors = False  # used to ignore repeated bit-errors in ERROR_PASSIVE

        # Per-ECU error-flag emission (to model ACTIVE vs PASSIVE behaviour correctly)
        #   - ERR_ACTIVE: drives the bus dominant (0) and will force an error-frame
        #   - ERR_PASSIVE: drives recessive (1) and does NOT affect the bus if another sender drives dominant
        self._tx_mode: str = "NORMAL"  # NORMAL | ERR_ACTIVE | ERR_PASSIVE
        self._err_flag_bits_left: int = 0
        self.master.register_slave(self)

    def start(self):
        print(f"[{self.name}] START slave_id={self.slave_id} ID=0x{self.arb_id:03X} period={self.tx_period:.2f}s")
        self.next_tx_time = time.time() + self.start_delay
        self._rx_thread.start()
        if self.auto_tx:
            self._tx_thread.start()

    def request_once(self, data: bytes, *, arbitration_id: Optional[int] = None):
        """Queue exactly one transmission (used for deterministic tests)."""
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

    def stop(self):
        self._stop = True

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
        elif self.tec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    # ---- Master-facing API ----

    def is_bus_off(self) -> bool:
        return self.state is NodeState.BUS_OFF

    def has_pending_frame(self) -> bool:
        return (self._pending_req is not None) and (self._bitstream is not None) and (not self.is_bus_off())

    def begin_frame_if_needed(self):
        """Ensure bitstream is ready for a pending request."""
        if self._pending_req is None or self._bitstream is not None:
            return
        self._bitstream = CANBitStream(self._pending_req.arbitration_id, self._pending_req.data, r0=BitValue.RECESSIVE)
        self._cursor = 0


    def _enter_error_flag(self, *, active: bool):
        """Stop sending the frame and start emitting an error flag (ACTIVE=dominant, PASSIVE=recessive)."""
        self._silence_bit_errors = True
        self._tx_mode = "ERR_ACTIVE" if active else "ERR_PASSIVE"
        self._err_flag_bits_left = 6  # in this simulator we use 6 bits as requested
        # Consider the attempt concluded: do not keep the request pending (respects tx_period scheduling)
        self._pending_req = None
        self._bitstream = None
        self._cursor = 0

    def is_emitting_error_flag_active(self) -> bool:
        return self._tx_mode == "ERR_ACTIVE"

    def peek_next_bit(self) -> Optional[Tuple[BitValue, Field]]:
        # If we are emitting an error flag, output it ONLY for the configured number of bits.
        # After that, this ECU stops contributing bits to the bus (as requested).
        if self._tx_mode == "ERR_ACTIVE":
            if self._err_flag_bits_left <= 0:
                return None
            return BitValue.DOMINANT, Field.DATA
        if self._tx_mode == "ERR_PASSIVE":
            if self._err_flag_bits_left <= 0:
                return None
            return BitValue.RECESSIVE, Field.DATA

        if not self.has_pending_frame():
            return None
        assert self._bitstream is not None
        if self._cursor >= len(self._bitstream.bits):
            return None
        return self._bitstream.bits[self._cursor], self._bitstream.fields[self._cursor]
    def advance(self):
        # During error-flag emission, we do not advance the original frame.
        if self._tx_mode in {"ERR_ACTIVE", "ERR_PASSIVE"}:
            if self._err_flag_bits_left > 0:
                self._err_flag_bits_left -= 1
            return
        self._cursor += 1

    def reset_for_retransmission(self):
        self._cursor = 0
        self._currently_transmitting = False
        self._tx_mode = "NORMAL"
        self._err_flag_bits_left = 0

    def mark_as_transmitting(self, value: bool):
        self._currently_transmitting = value

    def on_bus_bit(self, bus_bit: BitValue, field: Field, *, arbitration_window: bool):
        """Bit monitoring for the *current transmitter*."""
        if not self._currently_transmitting:
            return
        # Once an ECU has entered error-flag emission, it must not keep reporting bit errors.
        if self._tx_mode in {"ERR_ACTIVE", "ERR_PASSIVE"}:
            return
        if self._silence_bit_errors:
            return
        nxt = self.peek_next_bit()
        if nxt is None:
            return
        sent_bit, _sent_field = nxt
        if sent_bit is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
            if arbitration_window:
                return
            self.master.report_bit_error(self.slave_id, offender="bit_monitoring")

    def apply_error_update(self, *, tec_delta: int = 0, rec_delta: int = 0):
        self.tec = max(0, self.tec + tec_delta)
        self.rec = max(0, self.rec + rec_delta)
        self._update_state()

    def apply_success_update(self):
        """Chiamato dopo trasmissione con successo: TEC -= 1"""
        self.tec = max(0, self.tec - 1)
        self._update_state()

    def get_time_until_tx(self) -> float:
        """Ritorna il tempo rimanente prima della prossima trasmissione (in secondi)."""
        return max(0.0, self.next_tx_time - time.time())

    # ---- Internal threads ----

    def _tx_loop(self):
        if not self.auto_tx:
            return
        
        while not self._stop:
            if self.is_bus_off():
                time.sleep(0.2)
                continue
            
            now = time.time()
            if now >= self.next_tx_time:
                # Crea una nuova richiesta solo se non ce n'è una pendente
                if self._pending_req is None:
                    data = bytes([self.slave_id] * 8)  # Dati identificativi
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
                    print(f"[{self.name}] VUOLE TRASMETTERE (ID=0x{self.arb_id:03X}) TEC={self.tec} REC={self.rec} State={self.state.name}")
                
                # Programma la prossima trasmissione
                self.next_tx_time = now + self.tx_period
            
            time.sleep(0.05)

    def _rx_loop(self):
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, timeout=0.1)
            if bt is None:
                continue


class CANMaster:
    def __init__(
        self,
        tick_ms: float = 0.1,
        forward_to_socketcan: bool = False,
        can_channel: str = "vcan0",
        fault_injector: Optional[FaultInjector] = None,
        gather_window_s: float = 0.30,
    ):
        self.tick = tick_ms / 1000.0
        self.state = MasterState.IDLE
        self.clock = 0

        self.slaves: Dict[int, BaseECU] = {}
        self.bit_queues: Dict[int, "queue.Queue[BitTransmission]"] = {}
        self._pending_starts: "queue.Queue[TransmissionRequest]" = queue.Queue()

        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._status_thread = threading.Thread(target=self._status_loop, daemon=True)

        # Bus activity
        self._contenders: List[int] = []
        self._active_senders: List[int] = []
        self._winner: Optional[int] = None
        self._current_field: Field = Field.INTERMISSION
        self._arbitration_window = False
        
        # Arbitration gather window (to simulate the master "waiting a bit" to collect contenders)
        self.gather_window_s = float(gather_window_s)
        self._collecting = False
        self._collect_deadline = 0.0
        self._collect_contenders: set[int] = set()
        
        # Error handling
        self._error_senders: List[int] = []  # Tutte le ECU che devono mandare error flag
        self._passive_error_senders: set[int] = set()  # ECU che hanno segnalato un PASSIVE bit error in questo frame
        self._error_flag_bits_left = 0
        self._error_delim_bits_left = 0
        self._frame_ok = True

        # Per-frame ACTIVE error handling (modelled inside TRANSMIT, not as a global immediate abort)
        self._active_error_frame = False
        self._error_flag_ticks = 0  # counts emitted ACTIVE error-flag bits
        self._rec_bumped_for_error = False

        self._fault = fault_injector or FaultInjector()

        # SocketCAN
        self.forward = bool(forward_to_socketcan and CAN_AVAILABLE)
        self.hw_bus = None
        self.can_channel = can_channel
        if self.forward:
            try:
                self.hw_bus = can.interface.Bus(channel=can_channel, interface="socketcan")
                print(f"[MASTER] SocketCAN enabled on {can_channel}")
            except Exception as e:
                print(f"[MASTER] SocketCAN init failed: {e}")
                self.forward = False

    def register_slave(self, ecu: BaseECU):
        self.slaves[ecu.slave_id] = ecu
        self.bit_queues[ecu.slave_id] = queue.Queue()

    def submit_request(self, req: TransmissionRequest):
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
        self._status_thread.start()

    def stop(self):
        self._stop = True
        self._thread.join(timeout=2)
        if self.hw_bus:
            try:
                self.hw_bus.shutdown()
            except Exception:
                pass
        print("[MASTER] STOP")

    def _status_loop(self):
        """Thread separato per stampare lo stato periodicamente."""
        while not self._stop:
            time.sleep(3.0)  # Ogni 3 secondi
            
            if self.state == MasterState.IDLE:
                print(f"\n{'='*100}")
                print(f"STATUS BUS (IDLE)")
                print(f"{'='*100}")
                
                for sid in sorted(self.slaves.keys()):
                    ecu = self.slaves[sid]
                    time_left = ecu.get_time_until_tx()
                    
                    if ecu.is_bus_off():
                        status = "BUS-OFF"
                    elif ecu._pending_req is not None:
                        status = "PENDING"
                    elif time_left > 0:
                        status = f"Attende {time_left:.2f}s"
                    else:
                        status = "PRONTA"
                    
                    print(f"  [{ecu.name:6s}] ID=0x{ecu.arb_id:03X} | TEC={ecu.tec:3d} REC={ecu.rec:3d} | {ecu.state.name:13s} | {status}")
                
                print(f"{'='*100}\n")

    # ---- Error reporting ----

    def report_bit_error(self, sender_slave_id: int, offender: str = "unknown"):
        """Called by an ECU when it detects a bit-monitoring error.

        IMPORTANT behavioural model (as requested):
        - If the sender is ERROR_ACTIVE at the moment it detects the error, it emits an ACTIVE error flag (dominant 0),
          which forces an error on the bus. Other transmitters may detect it later (e.g., due to bit-stuffing).
        - If the sender is ERROR_PASSIVE at the moment it detects the error, it emits a PASSIVE error flag (recessive 1),
          which does NOT disturb the bus when another transmitter keeps driving dominant bits. The frame may still complete OK.
        """
        sender = self.slaves.get(sender_slave_id)
        if sender is None or sender.is_bus_off():
            return

        # If it already switched to an error-flag mode, ignore repeated notifications.
        if getattr(sender, "_tx_mode", "NORMAL") != "NORMAL":
            return
        if getattr(sender, "_silence_bit_errors", False):
            return

        pre_state = sender.state

        # -------------------------------
        # ERROR PASSIVE: send recessive error flag, do NOT abort the frame
        # -------------------------------
        if pre_state is NodeState.ERROR_PASSIVE:
            print(f"\n[MASTER] BIT ERROR (PASSIVE) rilevato da {sender.name} (offender={offender}) -> error flag recessivo, frame continua")
            sender.apply_error_update(tec_delta=8)
            sender._enter_error_flag(active=False)
            print(f"[MASTER] {sender.name}: TEC={sender.tec} (+8 per errore PASSIVE) State={sender.state.name}")
            return

        # -------------------------------
        # ERROR ACTIVE: send dominant error flag, frame becomes an error-frame
        # -------------------------------
        print(f"\n[MASTER] BIT ERROR (ACTIVE) rilevato da {sender.name} (offender={offender}) -> error flag dominante, frame abortito")
        self._frame_ok = False
        self._active_error_frame = True

        sender.apply_error_update(tec_delta=8)
        sender._enter_error_flag(active=True)
        print(f"[MASTER] {sender.name}: TEC={sender.tec} (+8 per errore ACTIVE) State={sender.state.name}")

        # REC +1 for listeners (only once per error-frame)
        if not self._rec_bumped_for_error:
            active_set = set(self._active_senders or [])
            for sid, ecu in self.slaves.items():
                if ecu.is_bus_off():
                    continue
                if sid in active_set:
                    continue
                ecu.rec = max(0, ecu.rec + 1)
            self._rec_bumped_for_error = True
    def _loop(self):
        while not self._stop:
            self.clock += 1
            if self.state == MasterState.IDLE:
                self._handle_idle()
            elif self.state == MasterState.ARBITRATION:
                self._handle_arbitration_step()
            elif self.state == MasterState.TRANSMIT:
                self._handle_transmit_step()
            elif self.state == MasterState.ERROR_FLAG:
                self._handle_error_flag_step()
            elif self.state == MasterState.ERROR_DELIM:
                self._handle_error_delim_step()
            elif self.state == MasterState.EOF:
                self._handle_eof()
            elif self.state == MasterState.INTERFRAME:
                self._handle_interframe()

            time.sleep(self.tick)

    def _drain_start_intents(self) -> List[int]:
        """Collect ALL pending start intents."""
        new_contenders: List[int] = []
        while True:
            try:
                req = self._pending_starts.get_nowait()
            except queue.Empty:
                break
            ecu = self.slaves.get(req.slave_id)
            if ecu is None or ecu.is_bus_off():
                continue
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
        # 1) Always drain new start intents (ECU that just asked to transmit).
        #    NOTE: we must NOT rely only on this queue, because requests can arrive
        #    while the bus is busy (TRANSMIT/ARBITRATION). In that case the ECU is
        #    already in PENDING, but its intent might have been drained earlier.
        self._drain_start_intents()

        now = time.time()

        # 2) Contenders are ALL ECU that currently have a pending frame.
        pending_ids = [
            sid
            for sid, ecu in self.slaves.items()
            if (not ecu.is_bus_off()) and ecu.has_pending_frame()
        ]

        # 3) If no one is pending, nothing to do.
        if not pending_ids and not self._collecting:
            return

        # 4) Start or continue the gather window.
        if not self._collecting:
            self._collecting = True
            self._collect_deadline = now + self.gather_window_s
            self._collect_contenders = set(pending_ids)

            names = ", ".join(self.slaves[s].name for s in self._collect_contenders)
            print(
                f"[MASTER] IDLE: gather window ({self.gather_window_s:.2f}s) | Pending now: {names if names else '-'}"
            )
            return

        # Collect new contenders that became pending during the window.
        self._collect_contenders |= set(pending_ids)

        # If (for any reason) nobody is pending anymore, stop collecting.
        if not self._collect_contenders:
            self._collecting = False
            return

        # Wait until the gather window expires.
        if now < self._collect_deadline:
            return

        # 5) Window expired -> start arbitration with everything collected.
        contenders = list(self._collect_contenders)
        self._collecting = False
        self._collect_contenders = set()

        self._contenders = list(dict.fromkeys(contenders))
        self._winner = None
        self._active_senders = []
        self._frame_ok = True
        self._error_senders = []
        self._fault.on_new_frame()

        # Prepare all ECU for arbitration (bitstream ready).
        for sid in self._contenders:
            self.slaves[sid].begin_frame_if_needed()
            self.slaves[sid].reset_for_retransmission()

        names = ", ".join(self.slaves[s].name for s in self._contenders)
        print()
        print(f"[MASTER] IDLE->ARBITRATION | Contenders: {names}")
        self.state = MasterState.ARBITRATION

    def _get_arbitration_bit(self, ecu: BaseECU) -> Optional[Tuple[BitValue, Field]]:
        nxt = ecu.peek_next_bit()
        if nxt is None:
            return None
        bit, field = nxt
        return bit, field

    def _handle_arbitration_step(self):
        self._arbitration_window = True

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
            self.state = MasterState.IDLE
            return

        bus_bit = BitValue.DOMINANT if any(b is BitValue.DOMINANT for _, b, _ in offered) else BitValue.RECESSIVE
        self._current_field = offered[0][2]
        bus_bit = self._fault.override_bus_bit(self._current_field, bus_bit)

        # Stampa bit per bit durante arbitraggio
        contenders_str = " | ".join([f"{self.slaves[sid].name}={int(b)}" for sid, b, _ in offered])
        print(f"  [ARB] {self._current_field.name:12s} | {contenders_str} -> BUS={int(bus_bit)}")

        self._broadcast(bus_bit, sender_name="BUS", field=self._current_field)

        if self._current_field in {Field.ID, Field.RTR}:
            losers: List[int] = []
            for sid, b, _f in offered:
                if b is BitValue.RECESSIVE and bus_bit is BitValue.DOMINANT:
                    losers.append(sid)
            for sid in losers:
                ecu = self.slaves[sid]
                print(f"  [ARB] {ecu.name} perde arbitraggio")
                ecu.reset_for_retransmission()
                self._contenders.remove(sid)

        for sid, _b, _f in offered:
            if sid in self._contenders:
                self.slaves[sid].advance()

        if len(self._contenders) == 1:
            self._winner = self._contenders[0]
            self._active_senders = [self._winner]
            win_ecu = self.slaves[self._winner]
            win_ecu.mark_as_transmitting(True)
            print(f"[MASTER] WINNER: {win_ecu.name} (ID=0x{win_ecu.arb_id:03X}) -> TRANSMIT")
            # Reset per-frame error bookkeeping
            self._frame_ok = True
            self._active_error_frame = False
            self._error_flag_ticks = 0
            self._rec_bumped_for_error = False
            self._error_senders = []
            self.state = MasterState.TRANSMIT
            return

        if self._current_field == Field.RTR and len(self._contenders) > 1:
            self._active_senders = list(self._contenders)
            self._winner = self._active_senders[0]
            for sid in self._active_senders:
                self.slaves[sid].mark_as_transmitting(True)
            names = ",".join(self.slaves[s].name for s in self._active_senders)
            print(f"[MASTER] COLLISION! Stesso ID/RTR: {names} -> TRANSMIT (errore imminente)")
            # Reset per-frame error bookkeeping
            self._frame_ok = True
            self._active_error_frame = False
            self._error_flag_ticks = 0
            self._rec_bumped_for_error = False
            self._error_senders = []
            self.state = MasterState.TRANSMIT

    def _handle_transmit_step(self):
        assert self._winner is not None

        _ = self._drain_start_intents()

        if not self._active_senders:
            self._active_senders = [self._winner]

        offered: List[Tuple[int, BitValue, Field]] = []
        for sid in list(self._active_senders):
            ecu = self.slaves[sid]
            nxt = ecu.peek_next_bit()
            if nxt is None:
                continue
            b, f = nxt
            offered.append((sid, b, f))

        if not offered:
            for sid in self._active_senders:
                self.slaves[sid].mark_as_transmitting(False)
            self.state = MasterState.EOF
            return

        field = offered[0][2]
        if any(f != field for _sid, _b, f in offered):
            field = Field.STUFF
        self._current_field = field
        self._arbitration_window = field in {Field.SOF, Field.ID, Field.RTR}

        bus_bit = BitValue.DOMINANT if any(b is BitValue.DOMINANT for _sid, b, _f in offered) else BitValue.RECESSIVE
        bus_bit = self._fault.override_bus_bit(field, bus_bit)

        # Stampa bit per bit durante trasmissione
        if len(self._active_senders) > 1:
            senders_str = " | ".join([f"{self.slaves[sid].name}={int(b)}" for sid, b, _ in offered])
            print(f"  [TX]  {self._current_field.name:12s} | {senders_str} -> BUS={int(bus_bit)}")
        else:
            print(f"  [TX]  {self._current_field.name:12s} | {self.slaves[self._winner].name}={int(bus_bit)}")

        self._broadcast(bus_bit, sender_name="BUS", field=field)

        for sid, _b, _f in offered:
            self.slaves[sid].on_bus_bit(bus_bit, field, arbitration_window=self._arbitration_window)

        if self.state == MasterState.TRANSMIT:
            for sid, _b, _f in offered:
                self.slaves[sid].advance()
        # If an ACTIVE error flag is being emitted, count its bits and terminate the frame after 6 bits.
        has_active_err_flag = any(self.slaves[sid].is_emitting_error_flag_active() for sid, _b, _f in offered)
        if has_active_err_flag:
            self._error_flag_ticks += 1
            if self._error_flag_ticks >= 6:
                # Mark as error-frame so the existing EOF error handling is used.
                self._error_senders = list(set(self._active_senders or []))
                for sid in (self._active_senders or []):
                    self.slaves[sid].mark_as_transmitting(False)
                self.state = MasterState.EOF


    def _handle_error_flag_step(self):
        """Gestisce ERROR FLAG: ACTIVE (6 bit DOM) o PASSIVE (8 bit REC)"""
        if not self._error_senders:
            self.state = MasterState.ERROR_DELIM
            return
        
        # Determina il tipo di error flag da mandare
        active_senders = [sid for sid in self._error_senders if sid in self.slaves and self.slaves[sid].state is NodeState.ERROR_ACTIVE]
        passive_senders = [sid for sid in self._error_senders if sid in self.slaves and self.slaves[sid].state is NodeState.ERROR_PASSIVE]
        
        if active_senders:
            # ERROR FLAG ACTIVE: 6 bit DOMINANT
            flag_bit = BitValue.DOMINANT
            flag_type = "ACTIVE"
            senders_str = ", ".join([self.slaves[sid].name for sid in active_senders])
        else:
            # ERROR FLAG PASSIVE: 8 bit RECESSIVE
            flag_bit = BitValue.RECESSIVE
            flag_type = "PASSIVE"
            senders_str = ", ".join([self.slaves[sid].name for sid in passive_senders])
        
        print(f"  [ERR] ERROR_FLAG_{flag_type} | {senders_str} -> BUS={int(flag_bit)} (bit {7-self._error_flag_bits_left}/{'6' if flag_type=='ACTIVE' else '8'})")
        self._broadcast(flag_bit, sender_name="ERROR", field=Field.STUFF)
        
        self._error_flag_bits_left -= 1
        
        if self._error_flag_bits_left <= 0:
            # ERROR FLAG PASSIVE conta come successo: -1 TEC
            for sid in passive_senders:
                ecu = self.slaves[sid]
                ecu.apply_success_update()
                print(f"[MASTER] {ecu.name}: TEC={ecu.tec} (-1 per ERROR_FLAG_PASSIVE trasmesso) State={ecu.state.name}")
            
            self.state = MasterState.ERROR_DELIM

    def _handle_error_delim_step(self):
        """Gestisce ERROR DELIMITER: 8 bit RECESSIVE"""
        if self._error_delim_bits_left <= 0:
            self.state = MasterState.INTERFRAME
            return
        
        delim_bit = BitValue.RECESSIVE
        print(f"  [ERR] ERROR_DELIM | BUS={int(delim_bit)} (bit {9-self._error_delim_bits_left}/8)")
        self._broadcast(delim_bit, sender_name="ERROR_DELIM", field=Field.STUFF)
        
        self._error_delim_bits_left -= 1
        
        if self._error_delim_bits_left <= 0:
            self.state = MasterState.INTERFRAME

    def _handle_eof(self):
        if self._frame_ok and self._winner is not None:
            sender0 = self.slaves[self._winner]
            req0 = sender0._pending_req
            if req0 is not None:
                print(f"[MASTER] Frame OK: ID=0x{req0.arbitration_id:03X} data={req0.data.hex().upper()}")
                
                # CORREZIONE: TEC -= 1 dopo successo
                for sid in (self._active_senders or [self._winner]):
                    ecu = self.slaves[sid]
                    ecu.apply_success_update()
                    print(f"[MASTER] {ecu.name}: TEC={ecu.tec} (-1 per successo) State={ecu.state.name}")
                    ecu._pending_req = None
                    ecu._cursor = 0
                    ecu._bitstream = None
                # CORREZIONE: se la trasmissione va a buon fine, i nodi in ascolto riducono REC di 1
                for sid, ecu in self.slaves.items():
                    if sid in self._active_senders or ecu.is_bus_off():
                        continue
                    if ecu.rec > 0:
                        ecu.rec -= 1
                        print(f"[MASTER] {ecu.name}: REC={ecu.rec} (-1 per frame OK ricevuto)")
                
                if self.forward and self.hw_bus:
                    try:
                        msg = can.Message(arbitration_id=req0.arbitration_id, data=req0.data, is_extended_id=False)
                        self.hw_bus.send(msg)
                    except Exception as e:
                        print(f"[MASTER] SocketCAN send failed: {e}")
        else:
            if self._error_senders or self._active_error_frame:
                print(f"[MASTER] Frame ERROR -> Retransmission")
                if self.forward and self.hw_bus:
                    try:
                        msg = can.Message(arbitration_id=0, data=b"", is_error_frame=True)
                        self.hw_bus.send(msg)
                    except Exception as e:
                        print(f"[MASTER] SocketCAN error-frame send failed: {e}")

            if self._winner is not None:
                self.slaves[self._winner].reset_for_retransmission()

        self.state = MasterState.INTERFRAME

    def _handle_interframe(self):
        self._contenders = []
        self._active_senders = []
        self._winner = None
        self._error_senders = []
        self._frame_ok = True
        self._active_error_frame = False
        self._error_flag_ticks = 0
        self._rec_bumped_for_error = False
        # reset per-frame passive error bookkeeping
        self._passive_error_senders.clear()
        for ecu in self.slaves.values():
            ecu._silence_bit_errors = False
            ecu._tx_mode = "NORMAL"
            ecu._err_flag_bits_left = 0
        self.state = MasterState.IDLE


def main():
    print("=" * 100)
    print("CAN BUS SIMULATOR - DYNAMIC ARBITRATION TEST")
    print("=" * 100)
    print("\nConfigurazione:")
    print("  - ECU con ID MINORE (priorita ALTA) -> periodo MAGGIORE (trasmette MENO spesso)")
    print("  - ECU con ID MAGGIORE (priorita BASSA) -> periodo MINORE (trasmette PIU spesso)")
    print("  - 2 ECU con STESSO ID -> generano COLLISION e incrementano TEC\n")
    print("\nScenari testati:")
    print("  1. ECU singola che trasmette da sola")
    print("  2. Arbitraggio tra ECU con ID diversi")
    print("  3. Collision tra ECU con stesso ID")
    print("  4. ECU che vuole trasmettere mentre un'altra sta trasmettendo\n")
    print("\nCORREZIONI IMPLEMENTATE:")
    print("  - START_SLOT eliminato: tutte le ECU PENDING partecipano SUBITO all'arbitraggio")
    print("  - Collision: ENTRAMBE le ECU incrementano TEC di +8")
    print("  - ERROR FLAG ACTIVE: 6 bit DOMINANT (TEC < 128)")
    print("  - ERROR FLAG PASSIVE: 8 bit RECESSIVE (TEC >= 128)")
    print("  - TEC -= 1 dopo trasmissione con successo")
    print("  - ERROR FLAG PASSIVE: +8 errore, -1 successo = +7 netto\n")

    master = CANMaster(
        tick_ms=0.5,
        forward_to_socketcan=False,
        can_channel="vcan0",
        fault_injector=None,
    )
    master.start()

    # ========================================
    # CONFIGURAZIONE ECU - TIMING OTTIMIZZATI
    # ========================================
    # Timing calcolati per garantire sovrapposizioni:
    # T=0s: ECU_A parte (scenario 1: trasmissione singola)
    # T=2s: ECU_B e ECU_C partono insieme (scenario 2: arbitraggio ID diversi)
    # T=4s: ECU_D e ECU_E partono insieme (scenario 3: collision stesso ID)
    # T=6s: ECU_A ritrasmette (scenario 4: sovrapposizione con altre ECU)
    
    # ECU_A: ID basso (0x050) -> priorita ALTA -> periodo 6s, parte subito
    ecu_a = BaseECU("ECU_A", 1, 0x050, master, tx_period=6.0, start_delay=0.1, auto_tx=True)
    
    # ECU_B: ID medio-basso (0x100) -> priorita MEDIA-ALTA -> periodo 8s, parte a 2s
    ecu_b = BaseECU("ECU_B", 2, 0x100, master, tx_period=8.0, start_delay=2.0, auto_tx=True)
    
    # ECU_C: ID medio-alto (0x200) -> priorita MEDIA-BASSA -> periodo 10s, parte a 2s (con ECU_B)
    ecu_c = BaseECU("ECU_C", 3, 0x200, master, tx_period=10.0, start_delay=2.0, auto_tx=True)
    
    # ECU_D: ID alto (0x300) -> priorita BASSA -> periodo 12s, parte a 4s
    ecu_d = BaseECU("ECU_D", 4, 0x300, master, tx_period=14.0, start_delay=4.0, auto_tx=True)
    
    # ECU_E: STESSO ID di ECU_D (0x300) -> COLLISION! -> periodo 14s, parte a 4s (con ECU_D)
    ecu_e = BaseECU("ECU_E", 5, 0x300, master, tx_period=14.0, start_delay=4.0, auto_tx=True)

    print("ECU configurate:")
    print(f"  - ECU_A: ID=0x050 (priorita ALTA)        -> TX ogni 6.0s  (start: 0.1s)")
    print(f"  - ECU_B: ID=0x100 (priorita MEDIA-ALTA)  -> TX ogni 8.0s  (start: 2.0s)")
    print(f"  - ECU_C: ID=0x200 (priorita MEDIA-BASSA) -> TX ogni 10.0s (start: 2.0s)")
    print(f"  - ECU_D: ID=0x300 (priorita BASSA)       -> TX ogni 12.0s (start: 4.0s)")
    print(f"  - ECU_E: ID=0x300 (COLLISION con D!)     -> TX ogni 14.0s (start: 4.0s)")
    print("\n" + "=" * 100)

    ecu_a.start()
    ecu_b.start()
    ecu_c.start()
    ecu_d.start()
    ecu_e.start()

    print("\nSimulazione avviata! (Ctrl+C per fermare)\n")

    try:
        while True:
            time.sleep(1.0)
            
            # Check BUS-OFF
            if any(ecu.is_bus_off() for ecu in [ecu_a, ecu_b, ecu_c, ecu_d, ecu_e]):
                print(f"\n{'*'*100}")
                print(f"BUS-OFF RILEVATO!")
                print(f"{'*'*100}")
                print(f"  ECU_A: TEC={ecu_a.tec:3d} REC={ecu_a.rec:3d} State={ecu_a.state.name}")
                print(f"  ECU_B: TEC={ecu_b.tec:3d} REC={ecu_b.rec:3d} State={ecu_b.state.name}")
                print(f"  ECU_C: TEC={ecu_c.tec:3d} REC={ecu_c.rec:3d} State={ecu_c.state.name}")
                print(f"  ECU_D: TEC={ecu_d.tec:3d} REC={ecu_d.rec:3d} State={ecu_d.state.name}")
                print(f"  ECU_E: TEC={ecu_e.tec:3d} REC={ecu_e.rec:3d} State={ecu_e.state.name}")
                print(f"{'*'*100}")
                break
            
    except KeyboardInterrupt:
        print("\n\nSimulazione interrotta manualmente")

    # Cleanup
    print(f"\n{'='*100}")
    print("[FINAL STATUS]")
    print(f"{'='*100}")
    print(f"  ECU_A: TEC={ecu_a.tec:3d} REC={ecu_a.rec:3d} State={ecu_a.state.name}")
    print(f"  ECU_B: TEC={ecu_b.tec:3d} REC={ecu_b.rec:3d} State={ecu_b.state.name}")
    print(f"  ECU_C: TEC={ecu_c.tec:3d} REC={ecu_c.rec:3d} State={ecu_c.state.name}")
    print(f"  ECU_D: TEC={ecu_d.tec:3d} REC={ecu_d.rec:3d} State={ecu_d.state.name}")
    print(f"  ECU_E: TEC={ecu_e.tec:3d} REC={ecu_e.rec:3d} State={ecu_e.state.name}")
    print(f"{'='*100}\n")

    ecu_a.stop()
    ecu_b.stop()
    ecu_c.stop()
    ecu_d.stop()
    ecu_e.stop()
    master.stop()


if __name__ == "__main__":
    main()
