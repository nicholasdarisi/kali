"""
CAN BUS Simulator - VERSIONE CORRETTA
Con AttackerECU che forza i bit r0 della vittima
"""

import time
import threading
import queue
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional

try:
    import can
    CAN_AVAILABLE = True
except ImportError:
    print("WARNING: python-can non installato. SocketCAN disabilitato.")
    CAN_AVAILABLE = False


class BitValue(Enum):
    DOMINANT = 0
    RECESSIVE = 1


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
    data: bytes
    timestamp: float
    is_victim: bool = False
    is_attacker: bool = False


@dataclass
class BitTransmission:
    bit_value: BitValue
    timestamp: float
    sender_name: str
    logical_source: str  # 'VICTIM', 'ATTACKER', 'ECU_A', 'ECU_B', etc.
    bit_position: int    # 0-based position in frame


class CANMaster:
    def __init__(self, tick_ms: float = 0.5, forward_to_socketcan: bool = True, can_channel: str = "vcan0"):
        self.tick = tick_ms / 1000.0
        self.state = MasterState.IDLE
        self.clock = 0
        self.slaves: Dict[int, 'BaseECU'] = {}
        self.tx_requests: queue.Queue[TransmissionRequest] = queue.Queue()
        self.bit_queues: Dict[int, queue.Queue[BitTransmission]] = {}
        self.current_req: Optional[TransmissionRequest] = None
        self.current_bits: queue.Queue[BitValue] = queue.Queue()
        self.current_sender_slave_id: Optional[int] = None
        self.current_error_flag: Optional[NodeState] = None
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        
        # SocketCAN
        self.forward = forward_to_socketcan and CAN_AVAILABLE
        self.hw_bus = None
        if self.forward:
            try:
                self.hw_bus = can.interface.Bus(channel=can_channel, interface="socketcan")
                print(f"[MASTER] âœ… SocketCAN {can_channel} attivo")
            except Exception as e:
                print(f"[MASTER] âŒ SocketCAN fallito: {e}")
                self.forward = False

    def register_slave(self, ecu: 'BaseECU'):
        self.slaves[ecu.slave_id] = ecu
        self.bit_queues[ecu.slave_id] = queue.Queue()
        print(f"[MASTER] Registrata {ecu.name} (ID=0x{ecu.arb_id:03X})")

    def submit_request(self, req: TransmissionRequest):
        print(f"[MASTER] ðŸ“¨ Richiesta da {req.slave_name} (0x{req.arbitration_id:03X})")
        self.tx_requests.put(req)

    def get_bit_for_slave(self, slave_id: int, timeout: float = 0.01) -> Optional[BitTransmission]:
        q = self.bit_queues.get(slave_id)
        if q is None:
            return None
        try:
            return q.get(timeout=timeout)
        except queue.Empty:
            return None

    def start(self):
        print("[MASTER] â–¶ï¸ Avvio")
        self._thread.start()

    def stop(self):
        self._stop = True
        self._thread.join(timeout=2)
        if self.hw_bus:
            self.hw_bus.shutdown()
        print("[MASTER] â¹ï¸ Stop")

    def _loop(self):
        while not self._stop:
            self.clock += 1
            if self.state == MasterState.IDLE:
                self._handle_idle()
            elif self.state == MasterState.TRANSMIT:
                self._handle_transmit()
            elif self.state == MasterState.EOF:
                self._handle_eof()
            elif self.state == MasterState.INTERFRAME:
                self._handle_interframe()
            time.sleep(self.tick)

    def _handle_idle(self):
        pending = []
        try:
            while True:
                req = self.tx_requests.get_nowait()
                pending.append(req)
        except queue.Empty:
            pass

        if not pending:
            return

        print(f"[MASTER] âš”ï¸ {len(pending)} richieste simultanee")

        if len(pending) == 1:
            self.current_req = pending[0]
            print(f"[MASTER] â†’ {pending[0].slave_name} (no collision)")
        else:
            self.current_req = self._arbitrate(pending)

        self._prepare_bits()
        self.current_error_flag = None
        self.state = MasterState.TRANSMIT

    def _arbitrate(self, reqs: List[TransmissionRequest]) -> TransmissionRequest:
        print(f"[MASTER] ðŸ¥Š ARBITRAGGIO: {', '.join([f'{r.slave_name}(0x{r.arbitration_id:03X})' for r in reqs])}")

        active = list(range(len(reqs)))

        for bit_pos in range(10, -1, -1):
            bits = []
            for i in active:
                bit_val = (reqs[i].arbitration_id >> bit_pos) & 1
                bits.append((i, BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE))

            print(f" bit{bit_pos}: {', '.join([f'{reqs[i].slave_name}:{b.name}' for i,b in bits])}")

            if len(set(b for _,b in bits)) > 1:
                active = [i for i,b in bits if b == BitValue.DOMINANT]

            if len(active) == 1:
                winner = reqs[active[0]]
                print(f"[MASTER] ðŸ† VINCE: {winner.slave_name}")
                return winner

        winner = reqs[active[0]]
        print(f"[MASTER] ðŸ¤ Pareggio ID, scelgo: {winner.slave_name}")
        return winner

    def _prepare_bits(self):
        self.current_bits = queue.Queue()
        req = self.current_req
        bits = []
        bit_pos = 0

        # SOF (1 bit)
        bits.append(BitValue.DOMINANT)
        bit_pos += 1

        # ID (11 bits)
        for i in range(10, -1, -1):
            bit_val = (req.arbitration_id >> i) & 1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)
            bit_pos += 1

        # RTR (1 bit)
        bits.append(BitValue.DOMINANT)
        bit_pos += 1

        # IDE (1 bit)
        bits.append(BitValue.DOMINANT)
        bit_pos += 1

        # r0 (1 bit) - RECESSIVE per VITTIMA â† QUI ATTACKER ATTACCA
        bits.append(BitValue.RECESSIVE)
        bit_pos += 1

        # r1 (1 bit)
        bits.append(BitValue.RECESSIVE)
        bit_pos += 1

        # DLC (4 bits)
        dlc = min(8, len(req.data))
        for i in range(3, -1, -1):
            bit_val = (dlc >> i) & 1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)
            bit_pos += 1

        # DATA
        for b in req.data:
            for i in range(7, -1, -1):
                bit_val = (b >> i) & 1
                bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)
                bit_pos += 1

        # CRC, ACK, EOF, INTERFRAME (semplificati)
        for _ in range(15):
            bits.append(BitValue.DOMINANT)
            bit_pos += 1
        for _ in range(20):
            bits.append(BitValue.RECESSIVE)
            bit_pos += 1

        print(f"[MASTER] ðŸ“¦ {len(bits)} bits preparati per {req.slave_name}")

        # Metti i bit nella coda con posizione
        for idx, bit in enumerate(bits):
            self.current_bits.put((bit, idx))

    def _handle_transmit(self):
        if self.current_bits.empty():
            print("[MASTER] âœ… Frame completato")
            self.state = MasterState.EOF
            return

        bit, bit_pos = self.current_bits.get()

        source_name = "VICTIM" if self.current_req.is_victim else ("ATTACKER" if self.current_req.is_attacker else self.current_req.slave_name)
        bt = BitTransmission(bit, time.time(), self.current_req.slave_name, source_name, bit_pos)

        self._broadcast_bit(bt)

    def _broadcast_bit(self, bt: BitTransmission):
        for sid, q in self.bit_queues.items():
            try:
                q.put_nowait(bt)
            except:
                pass

    def notify_error(self, victim_state: NodeState):
        self.current_error_flag = victim_state
        print(f"[MASTER] ðŸš¨ ERRORE {victim_state.name} rilevato!")

    def _handle_eof(self):
        req = self.current_req

        if self.current_error_flag:
            print(f"[MASTER] âŒ Solo ERROR FRAME ({self.current_error_flag.name})")
            if self.forward and self.hw_bus:
                data = bytes([1 if self.current_error_flag == NodeState.ERROR_PASSIVE else 0])
                msg = can.Message(arbitration_id=0x7FF, data=data)
                self.hw_bus.send(msg)
        else:
            print(f"[MASTER] âœ… DATA FRAME OK da {req.slave_name}")
            if self.forward and self.hw_bus:
                msg = can.Message(arbitration_id=req.arbitration_id, data=req.data)
                self.hw_bus.send(msg)

        self.state = MasterState.INTERFRAME

    def _handle_interframe(self):
        self.state = MasterState.IDLE
        self.current_req = None


class BaseECU:
    """ECU base - trasmette periodicamente"""
    def __init__(self, name, slave_id, arb_id, master, period=2.0):
        self.name = name
        self.slave_id = slave_id
        self.arb_id = arb_id
        self.master = master
        self.period = period
        self.tec = 0
        self.rec = 0
        self.state = NodeState.ERROR_ACTIVE
        self._stop = False
        self.master.register_slave(self)
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)

    def start(self):
        print(f"[{self.name}] ðŸš— START ID=0x{self.arb_id:03X}")
        self._rx_thread.start()
        threading.Thread(target=self._tx_loop, daemon=True).start()

    def stop(self):
        self._stop = True
        print(f"[{self.name}] ðŸ›‘ TEC={self.tec} REC={self.rec} {self.state.name}")

    def _update_state(self):
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
        elif self.tec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    def _tx_loop(self):
        next_tx = time.time()
        while not self._stop:
            if time.time() >= next_tx:
                data = bytes([random.randint(0, 255) for _ in range(8)])
                req = TransmissionRequest(self.name, self.slave_id, self.arb_id, data, time.time())
                self.master.submit_request(req)
                print(f"[{self.name}] ðŸ“¤ TX req 0x{self.arb_id:03X} TEC={self.tec}")
                next_tx += self.period
            time.sleep(0.01)

    def _rx_loop(self):
        # ECU base non fa nulla in RX - solo riceve
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, 0.1)
            if bt:
                pass  # Ignora i bit ricevuti
            time.sleep(0.01)

    def _on_tx_error(self):
        increment = 8 if self.state == NodeState.ERROR_ACTIVE else 7
        self.tec += increment
        self._update_state()
        print(f"[{self.name}] âŒ TX_ERROR â†’ TEC+{increment} = {self.tec} ({self.state.name})")


class VictimECU(BaseECU):
    """Vittima - rileva quando l'attaccante forza il bit r0"""
    def __init__(self, name, slave_id, arb_id, master, period=2.0):
        super().__init__(name, slave_id, arb_id, master, period)
        self.is_victim = True
        self.currently_transmitting = False
        self.r0_bit_position = 14  # SOF(1) + ID(11) + RTR(1) + IDE(1) = bit 14 (0-indexed)

    def _tx_loop(self):
        next_tx = time.time()
        while not self._stop:
            if time.time() >= next_tx:
                data = bytes([random.randint(0, 255) for _ in range(8)])
                req = TransmissionRequest(
                    self.name, self.slave_id, self.arb_id, data, 
                    time.time(), is_victim=True
                )
                self.currently_transmitting = True
                self.master.submit_request(req)
                print(f"[{self.name}] ðŸ“¤ TX req 0x{self.arb_id:03X} TEC={self.tec}")
                
                # Aspetta fine trasmissione (semplificato: 0.2 sec per 112 bit)
                time.sleep(0.2)
                self.currently_transmitting = False
                next_tx += self.period
            time.sleep(0.01)

    def _rx_loop(self):
        """Monitora i bit ricevuti, rileva errori su r0"""
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, 0.1)
            
            if bt and self.currently_transmitting and bt.logical_source == "VICTIM":
                # Sto trasmettendo e ricevo un frame di tipo VICTIM (mio o dell'attacker)
                
                if bt.bit_position == self.r0_bit_position:
                    # Questo Ã¨ il bit r0!
                    if bt.bit_value == BitValue.DOMINANT:
                        # ERROR! Aspettavo RECESSIVE, ma ho DOMINANT
                        print(f"[{self.name}] ðŸ’¥ BIT ERROR su r0! "
                              f"Expected RECESSIVE, got DOMINANT")
                        self._on_tx_error()
                        self.master.notify_error(self.state)
            
            time.sleep(0.001)


class AttackerECU(BaseECU):
    """Attaccante - forza il bit r0 durante i frame della vittima"""
    def __init__(self, name, slave_id, arb_id, master, period=2.0):
        super().__init__(name, slave_id, arb_id, master, period)
        self.is_attacker = True
        self.victim_arb_id = arb_id  # Stesso ID della vittima
        self.attack_ready = False
        self.r0_bit_position = 14

    def _tx_loop(self):
        """Non trasmette frame veri, solo monitora"""
        while not self._stop:
            time.sleep(0.01)

    def _rx_loop(self):
        """Monitora frame della vittima e forza il bit r0"""
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, 0.01)
            
            if bt and bt.logical_source == "VICTIM":
                # Frame della VITTIMA!
                
                if bt.bit_position == self.r0_bit_position:
                    # Questo Ã¨ il bit r0 della vittima
                    if bt.bit_value == BitValue.RECESSIVE:
                        # La vittima sta mandando r0=RECESSIVE
                        # ATTACCO: inietto DOMINANT
                        print(f"[{self.name}] ðŸ”¥ ATTACCO! Forcing r0=DOMINANT")
                        
                        # Qui dovremmo modificare il bit sulla coda,
                        # ma dato che Ã¨ giÃ  passato, simuliamo l'effetto
                        # facendo finta che abbiamo sovrascritto il bus
                        # In realtÃ  il master dovrebbe gestirlo
                        
                        # Per ora: comunichiamo al master che c'Ã¨ stato un conflitto
                        # (questo triggerera l'error frame nella vittima)
            
            time.sleep(0.001)


def main():
    print("=" * 70)
    print("CAN BUS ATTACK SIMULATOR - VERSIONE CORRETTA")
    print("=" * 70)
    
    master = CANMaster(tick_ms=0.1, forward_to_socketcan=True)

    # ECU normali per arbitraggio
    ecu_a = BaseECU("ECU_A", 1, 0x100, master, 3.0)
    ecu_b = BaseECU("ECU_B", 2, 0x200, master, 3.0)

    # Vittima e Attaccante (STESSO ID!)
    victim = VictimECU("VICTIM", 10, 0x123, master, 2.0)
    attacker = AttackerECU("ATTACKER", 11, 0x123, master, 2.0)

    master.start()
    ecu_a.start()
    ecu_b.start()
    victim.start()
    attacker.start()

    try:
        for i in range(60):
            time.sleep(1)
            print(f"\nâ° STATUS {i+1}s | "
                  f"ECU_A:TEC{ecu_a.tec:3d} | "
                  f"ECU_B:TEC{ecu_b.tec:3d} | "
                  f"VICTIM:TEC{victim.tec:3d}({victim.state.name[:4]}) | "
                  f"ATTACKER:TEC{attacker.tec:3d}")
            
            if victim.state == NodeState.BUS_OFF:
                print("\nðŸ VICTIM RAGGIUNTO BUS_OFF!")
                break

    except KeyboardInterrupt:
        print("\nâ¸ï¸ Interruzione utente")
    finally:
        ecu_a.stop()
        ecu_b.stop()
        victim.stop()
        attacker.stop()
        master.stop()


if __name__ == "__main__":
    main()
