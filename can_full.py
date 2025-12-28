"""
CAN BUS Master Controller - Orchestrates bit-level communication
Gestisce arbitraggio, trasmissione bit-per-bit, e sincronizzazione
"""

import threading
import time
import queue
from typing import Dict, List, Optional
from enum import Enum, auto
from dataclasses import dataclass


class BitValue(Enum):
    """Rappresentazione dei bit: DOMINANTE (0) o RECESSIVO (1)"""
    DOMINANT = 0    # bit 0 (vince l'arbitraggio)
    RECESSIVE = 1   # bit 1 (perde l'arbitraggio)


class MasterState(Enum):
    """Stati del Master"""
    IDLE = auto()
    ARBITRATION = auto()
    DATA_TRANSMISSION = auto()
    CRC_TRANSMISSION = auto()
    ACK_TRANSMISSION = auto()
    EOF = auto()
    INTERFRAME = auto()


@dataclass
class TransmissionRequest:
    """Richiesta di trasmissione da uno slave"""
    slave_name: str
    slave_id: int
    arbitration_id: int
    data: bytes
    timestamp: float


@dataclass
class BitTransmission:
    """Rappresenta la trasmissione di un singolo bit"""
    bit_value: BitValue
    timestamp: float
    sender_name: str


class CANMaster:
    """
    Master controller per simulazione CAN BUS a livello bit.
    """
    
    def __init__(self, tick_duration_ms: float = 1.0):
        self.tick_duration = tick_duration_ms / 1000.0
        self.clock_ticks = 0
        self.global_clock_ticks = 0
        
        self.slaves: Dict[int, 'CANSlave'] = {}
        
        self.tx_request_queue = queue.Queue()
        self.bit_distribution_queues: Dict[int, queue.Queue] = {}
        
        self.bus_state = MasterState.IDLE
        self.current_transmitter: Optional[int] = None
        self.arbitration_winners: List[int] = []
        
        self.tx_buffer: Optional[TransmissionRequest] = None
        self.tx_bit_queue: queue.Queue = queue.Queue()
        
        self._stop = False
        self._master_thread = threading.Thread(target=self._master_loop, daemon=True)
        self._lock = threading.RLock()
    
    def register_slave(self, slave_id: int, slave: 'CANSlave'):
        with self._lock:
            self.slaves[slave_id] = slave
            self.bit_distribution_queues[slave_id] = queue.Queue()
            print(f"[MASTER] Registrato slave: {slave.name} (ID={slave_id})")
    
    def request_transmission(self, request: TransmissionRequest):
        self.tx_request_queue.put(request)
    
    def get_received_bit(self, slave_id: int, timeout: float = 0.1) -> Optional[BitTransmission]:
        try:
            return self.bit_distribution_queues[slave_id].get(timeout=timeout)
        except queue.Empty:
            return None
    
    def start(self):
        print("[MASTER] Avvio Master Controller")
        self._master_thread.start()
    
    def stop(self):
        self._stop = True
        self._master_thread.join(timeout=2.0)
        print("[MASTER] Master Controller arrestato")
    
    def _master_loop(self):
        while not self._stop:
            try:
                now = time.time()
                self.global_clock_ticks += 1
                
                if self.bus_state == MasterState.IDLE:
                    self._handle_idle_state(now)
                elif self.bus_state in (MasterState.ARBITRATION, MasterState.DATA_TRANSMISSION,
                                       MasterState.CRC_TRANSMISSION, MasterState.ACK_TRANSMISSION):
                    self._handle_transmission_state(now)
                elif self.bus_state == MasterState.EOF:
                    self._handle_eof_state(now)
                elif self.bus_state == MasterState.INTERFRAME:
                    self._handle_interframe_state(now)
                
                self.clock_ticks += 1
                time.sleep(self.tick_duration)
                
            except Exception as e:
                print(f"[MASTER] Errore nel main loop: {e}")
                time.sleep(0.01)
    
    def _handle_idle_state(self, now: float):
        try:
            self.tx_buffer = self.tx_request_queue.get(timeout=0.01)
            print(f"[MASTER] Inizio ARBITRAGGIO per {self.tx_buffer.slave_name}")
            self.bus_state = MasterState.ARBITRATION
            self.arbitration_winners = [self.tx_buffer.slave_id]
            self._prepare_bit_queue(self.tx_buffer)
        except queue.Empty:
            pass
    
    def _prepare_bit_queue(self, request: TransmissionRequest):
        while not self.tx_bit_queue.empty():
            self.tx_bit_queue.get()
        
        bits = []
        
        # SOF
        bits.append(BitValue.DOMINANT)
        
        # Arbitration Field
        arb_bits = self._int_to_bits(request.arbitration_id, 11)
        bits.extend(arb_bits)
        bits.append(BitValue.DOMINANT)  # RTR = 0
        bits.append(BitValue.DOMINANT)  # IDE = 0
        
        # Control Field
        bits.append(BitValue.RECESSIVE)  # r0 = 1
        bits.append(BitValue.RECESSIVE)  # r1 = 1
        dlc_bits = self._int_to_bits(len(request.data), 4)
        bits.extend(dlc_bits)
        
        # Data Field
        for byte in request.data:
            byte_bits = self._int_to_bits(byte, 8)
            bits.extend(byte_bits)
        
        # CRC Field
        crc = self._calculate_crc(request.arbitration_id, request.data)
        crc_bits = self._int_to_bits(crc, 15)
        bits.extend(crc_bits)
        bits.append(BitValue.RECESSIVE)
        
        # ACK Field
        bits.append(BitValue.RECESSIVE)
        bits.append(BitValue.RECESSIVE)
        
        # EOF
        for _ in range(7):
            bits.append(BitValue.RECESSIVE)
        
        # IFS
        for _ in range(3):
            bits.append(BitValue.RECESSIVE)
        
        for bit in bits:
            self.tx_bit_queue.put(bit)
        
        print(f"[MASTER] Preparati {len(bits)} bit per trasmissione")
        self.bus_state = MasterState.DATA_TRANSMISSION
    
    def _handle_transmission_state(self, now: float):
        try:
            bit = self.tx_bit_queue.get(timeout=0.001)
            
            bit_tx = BitTransmission(
                bit_value=bit,
                timestamp=now,
                sender_name=self.slaves[self.arbitration_winners[0]].name
            )
            
            self._broadcast_bit(bit_tx)
            
            if self.tx_bit_queue.empty():
                print(f"[MASTER] Trasmissione completata, passo a EOF")
                self.bus_state = MasterState.EOF
        
        except queue.Empty:
            pass
    
    def _handle_eof_state(self, now: float):
        print(f"[MASTER] Fine trasmissione, attesa interframe...")
        self.bus_state = MasterState.INTERFRAME
        self.eof_start_time = now
    
    def _handle_interframe_state(self, now: float):
        if now - getattr(self, 'eof_start_time', now) > 0.05:
            print(f"[MASTER] Interframe completato, torno a IDLE")
            self.bus_state = MasterState.IDLE
            self.current_transmitter = None
            self.tx_buffer = None
    
    def _broadcast_bit(self, bit_tx: BitTransmission):
        for slave_id in self.slaves:
            if slave_id != self.arbitration_winners[0]:
                try:
                    self.bit_distribution_queues[slave_id].put(bit_tx)
                except queue.Full:
                    print(f"[MASTER] Coda piena per slave {slave_id}, bit scartato")
    
    @staticmethod
    def _int_to_bits(value: int, num_bits: int) -> List[BitValue]:
        bits = []
        for i in range(num_bits - 1, -1, -1):
            bit = (value >> i) & 1
            bits.append(BitValue.DOMINANT if bit == 0 else BitValue.RECESSIVE)
        return bits
    
    @staticmethod
    def _calculate_crc(arb_id: int, data: bytes) -> int:
        crc = 0
        crc ^= arb_id & 0xFFFF
        for byte in data:
            crc ^= byte
            crc = ((crc << 1) ^ (0x8005 if (crc & 0x8000) else 0)) & 0xFFFF
        return (crc >> 1) & 0x7FFF


class CANSlave:
    """Slave ECU - Comunica con il Master"""
    
    def __init__(
        self,
        name: str,
        slave_id: int,
        arbitration_id: int,
        master: CANMaster,
        period_sec: float = 5.0,
        initial_tec: int = 0,
        initial_rec: int = 0,
    ):
        self.name = name
        self.slave_id = slave_id
        self.arb_id = arbitration_id
        self.master = master
        self.period = period_sec
        
        self.tec = initial_tec
        self.rec = initial_rec
        self.state = "ERROR_ACTIVE"
        self._update_state()
        
        self.currently_transmitting = False
        self.last_tx_data = None
        self.last_tx_time = 0.0
        
        self.received_bits: List[BitTransmission] = []
        self.received_messages: queue.Queue = queue.Queue()
        
        self._stop = False
        self._tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        
        self.master.register_slave(self.slave_id, self)
    
    def start(self):
        print(f"[{self.name}] Avvio (ID=0x{self.arb_id:X}, state={self.state})")
        self._tx_thread.start()
        self._rx_thread.start()
    
    def stop(self):
        self._stop = True
        self._tx_thread.join(timeout=1.0)
        self._rx_thread.join(timeout=1.0)
        print(f"[{self.name}] Arrestato (TEC={self.tec}, REC={self.rec}, state={self.state})")
    
    def _update_state(self):
        if self.tec >= 256:
            self.state = "BUS_OFF"
        elif self.tec >= 128:
            self.state = "ERROR_PASSIVE"
        else:
            self.state = "ERROR_ACTIVE"
    
    def _on_tx_success(self):
        if self.tec > 0:
            self.tec -= 1
        self._update_state()
    
    def _on_tx_error(self):
        if self.state == "ERROR_ACTIVE":
            self.tec += 8
        elif self.state == "ERROR_PASSIVE":
            self.tec += 7
        self._update_state()
    
    def _on_rx_error_flag(self):
        self.rec += 1
        self._update_state()
    
    def _on_rx_success(self):
        if self.rec > 0:
            self.rec -= 1
        self._update_state()
    
    def _tx_loop(self):
        next_tx = time.time()
        
        while not self._stop:
            if self.state == "BUS_OFF":
                print(f"[{self.name}] BUS OFF: Impossibile trasmettere")
                time.sleep(1.0)
                continue
            
            now = time.time()
            
            if self.period > 0 and now >= next_tx:
                payload = self._build_payload()
                self.last_tx_data = payload
                self.last_tx_time = now
                self.currently_transmitting = True
                
                request = TransmissionRequest(
                    slave_name=self.name,
                    slave_id=self.slave_id,
                    arbitration_id=self.arb_id,
                    data=payload,
                    timestamp=now
                )
                
                print(f"[{self.name}] Richiedo trasmissione: data={payload.hex().upper()}")
                self.master.request_transmission(request)
                
                time.sleep(0.2)
                
                self._on_tx_success()
                print(f"[{self.name}] TX successo â†’ TEC={self.tec}")
                
                self.currently_transmitting = False
                next_tx += self.period
            
            time.sleep(0.01)
    
    def _rx_loop(self):
        while not self._stop:
            bit_tx = self.master.get_received_bit(self.slave_id, timeout=0.1)
            
            if bit_tx is not None:
                self.received_bits.append(bit_tx)
            
            time.sleep(0.001)
    
    def _build_payload(self) -> bytes:
        import random
        payload = bytearray(8)
        payload[0] = 0x20
        for i in range(1, 8):
            payload[i] = random.randint(0, 255)
        return bytes(payload)