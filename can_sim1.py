"""
CAN BUS Simulator - ATTACCO FUNZIONANTE
L'attaccante trasmette SIMULTANEAMENTE alla vittima con STESSO ID
per creare una collisione e forzare il bit r0
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
    logical_source: str  # 'VICTIM', 'ATTACKER', 'ECU_A', 'ECU_B'
    bit_position: int


class CANMaster:
    def __init__(self, tick_ms: float = 0.5, forward_to_socketcan: bool = False, can_channel: str = "vcan0"):
        self.tick = tick_ms / 1000.0
        self.state = MasterState.IDLE
        self.clock = 0
        self.slaves: Dict[int, 'BaseECU'] = {}
        self.tx_requests: queue.Queue[TransmissionRequest] = queue.Queue()
        self.bit_queues: Dict[int, queue.Queue[BitTransmission]] = {}
        self.current_req: Optional[TransmissionRequest] = None
        self.current_bits: List[tuple] = []  # (BitValue, position)
        self.current_bit_index: int = 0
        self.current_error_flag: Optional[NodeState] = None
        self._stop = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        
        # Per permettere all'attaccante di forzare il bit r0
        self.bit_override: Optional[BitValue] = None
        
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
        print(f"[MASTER] Registrata {ecu.name} (ID=0x{ecu.arb_id:03X}, slave_id={ecu.slave_id})")

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

        if len(pending) == 1:
            self.current_req = pending[0]
            print(f"[MASTER] â†’ {pending[0].slave_name} (no collision)")
        else:
            # Arbitraggio tra richieste simultanee
            self.current_req = self._arbitrate(pending)

        self._prepare_bits()
        self.current_error_flag = None
        self.current_bit_index = 0
        self.state = MasterState.TRANSMIT

    def _arbitrate(self, reqs: List[TransmissionRequest]) -> TransmissionRequest:
        print(f"[MASTER] ðŸ¥Š ARBITRAGGIO: {len(reqs)} candidati")
        active = list(range(len(reqs)))

        for bit_pos in range(10, -1, -1):
            bits = []
            for i in active:
                bit_val = (reqs[i].arbitration_id >> bit_pos) & 1
                bits.append((i, BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE))

            # Filtra solo i DOMINANT
            active = [i for i,b in bits if b == BitValue.DOMINANT]

            if len(active) == 1:
                winner = reqs[active[0]]
                print(f"[MASTER] ðŸ† VINCE: {winner.slave_name}")
                return winner

        winner = reqs[active[0]]
        print(f"[MASTER] ðŸ¤ Pareggio ID, scelgo: {winner.slave_name}")
        return winner

    def _prepare_bits(self):
        """Prepara i bit per la trasmissione"""
        bits = []
        req = self.current_req

        # SOF
        bits.append(BitValue.DOMINANT)

        # ID (11 bits)
        for i in range(10, -1, -1):
            bit_val = (req.arbitration_id >> i) & 1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # RTR
        bits.append(BitValue.DOMINANT)

        # IDE
        bits.append(BitValue.DOMINANT)

        # r0 â† QUI L'ATTACCANTE POTREBBE FORZARE!
        bits.append(BitValue.RECESSIVE)

        # r1
        bits.append(BitValue.RECESSIVE)

        # DLC (4 bits)
        dlc = min(8, len(req.data))
        for i in range(3, -1, -1):
            bit_val = (dlc >> i) & 1
            bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # DATA
        for b in req.data:
            for i in range(7, -1, -1):
                bit_val = (b >> i) & 1
                bits.append(BitValue.DOMINANT if bit_val == 0 else BitValue.RECESSIVE)

        # CRC, ACK, EOF (semplificati)
        for _ in range(15):
            bits.append(BitValue.DOMINANT)  # CRC
        for _ in range(20):
            bits.append(BitValue.RECESSIVE)  # EOF + INTERFRAME

        self.current_bits = [(bit, idx) for idx, bit in enumerate(bits)]
        print(f"[MASTER] ðŸ“¦ {len(bits)} bits preparati per {req.slave_name}")

    def _handle_transmit(self):
        """Trasmette un bit alla volta"""
        if self.current_bit_index >= len(self.current_bits):
            print("[MASTER] âœ… Frame completato")
            self.state = MasterState.EOF
            return

        bit, bit_pos = self.current_bits[self.current_bit_index]

        # âš ï¸ ATTACCANTE PUÃ’ FORZARE IL BIT r0
        if bit_pos == 14 and self.bit_override is not None:
            # Bit 14 Ã¨ r0 - attaccante lo forza
            bit = self.bit_override
            print(f"[MASTER] âš¡ BIT OVERRIDE su posizione {bit_pos}: {bit.name}")

        source_name = "VICTIM" if self.current_req.is_victim else ("ATTACKER" if self.current_req.is_attacker else self.current_req.slave_name)
        bt = BitTransmission(bit, time.time(), self.current_req.slave_name, source_name, bit_pos)

        # Broadcast a tutti gli ECU
        for sid, q in self.bit_queues.items():
            try:
                q.put_nowait(bt)
            except:
                pass

        self.current_bit_index += 1

    def set_bit_override(self, bit: Optional[BitValue]):
        """Permettere all'attaccante di forzare il bit r0"""
        self.bit_override = bit

    def notify_error(self, victim_state: NodeState):
        self.current_error_flag = victim_state
        print(f"[MASTER] ðŸš¨ ERRORE {victim_state.name} rilevato!")

    def _handle_eof(self):
        req = self.current_req

        if self.current_error_flag:
            print(f"[MASTER] âŒ Solo ERROR FRAME ({self.current_error_flag.name})")
        else:
            print(f"[MASTER] âœ… DATA FRAME OK da {req.slave_name}")

        self.state = MasterState.INTERFRAME

    def _handle_interframe(self):
        self.state = MasterState.IDLE
        self.current_req = None
        self.bit_override = None


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
        self.currently_transmitting = False
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
                self.currently_transmitting = True
                self.master.submit_request(req)
                print(f"[{self.name}] ðŸ“¤ TX req 0x{self.arb_id:03X}")
                
                # Aspetta ~200ms per il completamento della trasmissione (35 bit/ms)
                time.sleep(0.2)
                self.currently_transmitting = False
                next_tx += self.period
            time.sleep(0.01)

    def _rx_loop(self):
        """Monitora i bit ricevuti"""
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, 0.01)
            if bt:
                pass  # ECU base ignora i bit
            time.sleep(0.001)

    def _on_tx_error(self):
        increment = 8 if self.state == NodeState.ERROR_ACTIVE else 7
        self.tec += increment
        self._update_state()
        print(f"[{self.name}] âŒ TX_ERROR â†’ TEC+{increment} = {self.tec} ({self.state.name})")


class VictimECU(BaseECU):
    """Vittima - monitora il bit r0"""
    def __init__(self, name, slave_id, arb_id, master, period=2.0):
        super().__init__(name, slave_id, arb_id, master, period)
        self.r0_bit_position = 14

    def _rx_loop(self):
        """Monitora bit durante propria trasmissione"""
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, 0.01)
            
            if bt and self.currently_transmitting:
                # Se ricevo il bit r0 in posizione 14 durante trasmissione
                if bt.bit_position == self.r0_bit_position:
                    if bt.bit_value == BitValue.DOMINANT:
                        # âŒ ERRORE! Aspettavo RECESSIVE
                        print(f"[{self.name}] ðŸ’¥ BIT ERROR! r0=DOMINANT (expected RECESSIVE)")
                        self._on_tx_error()
                        self.master.notify_error(self.state)
            
            time.sleep(0.001)


class AttackerECU(BaseECU):
    """Attaccante - richiede TX simultaneamente alla vittima e forza il bit r0"""
    def __init__(self, name, slave_id, arb_id, master, victim_name="VICTIM", period=2.0):
        super().__init__(name, slave_id, arb_id, master, period)
        self.victim_name = victim_name
        self.victim_last_tx_time = 0
        self.attack_delay = 0.05  # Delay minimo per far coincidere le richieste

    def _tx_loop(self):
        """Monitora quando la vittima trasmette e attacca"""
        while not self._stop:
            # Cerca di monitorare quando la vittima richiede TX
            # Questo Ã¨ un'euristica: proviamo a trasmettere leggermente dopo la vittima
            time.sleep(0.01)

    def _rx_loop(self):
        """Monitora il bus e quando vede VICTIM che trasmette, forza il bit r0"""
        attack_window_open = False
        
        while not self._stop:
            bt = self.master.get_bit_for_slave(self.slave_id, 0.01)
            
            # Quando ricevo un frame della VICTIM, preparo l'attacco
            if bt and bt.logical_source == "VICTIM":
                # Ricevo un frame VICTIM - provo a forzare il bit r0
                if bt.bit_position == 14:  # r0
                    if bt.bit_value == BitValue.RECESSIVE:
                        # âœ… VICTIM sta inviando r0=RECESSIVE
                        # Forzo DOMINANT per creare conflitto
                        print(f"[{self.name}] ðŸ”¥ ATTACCO! Forcing r0=DOMINANT")
                        self.master.set_bit_override(BitValue.DOMINANT)
                        attack_window_open = True
                elif attack_window_open and bt.bit_position > 14:
                    # Fine della finestra di attacco
                    self.master.set_bit_override(None)
                    attack_window_open = False
            
            time.sleep(0.001)

    def request_attack(self):
        """Richiedi una trasmissione (attacco) simultanea"""
        data = bytes([random.randint(0, 255) for _ in range(8)])
        req = TransmissionRequest(
            self.name, self.slave_id, self.arb_id, data, 
            time.time(), is_attacker=True
        )
        self.master.submit_request(req)
        print(f"[{self.name}] ðŸŽ¯ Richiesta attacco simultaneo!")


class AttackCoordinator(threading.Thread):
    """Coordina gli attacchi dell'attaccante con le TX della vittima"""
    def __init__(self, attacker: AttackerECU, victim: VictimECU, master: CANMaster):
        super().__init__(daemon=True)
        self.attacker = attacker
        self.victim = victim
        self.master = master
        self._stop = False

    def run(self):
        """Monitora quando la vittima trasmette e coordina l'attacco"""
        victim_was_transmitting = False
        
        while not self._stop:
            if self.victim.currently_transmitting and not victim_was_transmitting:
                # âœ… VITTIMA INIZIA A TRASMETTERE
                # Attaccante deve richiedere TX SIMULTANEAMENTE
                print(f"[COORDINATOR] ðŸŽ¯ VICTIM sta trasmettendo - ATTACCO!")
                self.attacker.request_attack()
                victim_was_transmitting = True
            
            elif not self.victim.currently_transmitting and victim_was_transmitting:
                # VITTIMA ha finito di trasmettere
                victim_was_transmitting = False
            
            time.sleep(0.01)

    def stop(self):
        self._stop = True


def main():
    print("=" * 70)
    print("CAN BUS ATTACK SIMULATOR - VERSIONE CON ATTACCO COORDINATO")
    print("=" * 70)
    
    master = CANMaster(tick_ms=0.1, forward_to_socketcan=False)

    # ECU normali per arbitraggio
    ecu_a = BaseECU("ECU_A", 1, 0x100, master, 3.0)
    ecu_b = BaseECU("ECU_B", 2, 0x200, master, 3.0)

    # Vittima e Attaccante (STESSO ID!)
    victim = VictimECU("VICTIM", 10, 0x123, master, 2.0)
    attacker = AttackerECU("ATTACKER", 11, 0x123, master, "VICTIM", 2.0)

    # Coordinatore per sincronizzare l'attacco
    coordinator = AttackCoordinator(attacker, victim, master)

    master.start()
    ecu_a.start()
    ecu_b.start()
    victim.start()
    attacker.start()
    coordinator.start()

    try:
        for i in range(90):
            time.sleep(1)
            print(f"\nâ° STATUS {i+1}s | "
                  f"A:TEC{ecu_a.tec:3d} | "
                  f"B:TEC{ecu_b.tec:3d} | "
                  f"V:TEC{victim.tec:3d}({victim.state.name[:4]}) | "
                  f"ATK:TEC{attacker.tec:3d}")
            
            if victim.state == NodeState.BUS_OFF:
                print("\n" + "=" * 70)
                print("ðŸ VICTIM RAGGIUNTO BUS_OFF! ATTACCO RIUSCITO!")
                print("=" * 70)
                break

    except KeyboardInterrupt:
        print("\nâ¸ï¸ Interruzione utente")
    finally:
        coordinator.stop()
        ecu_a.stop()
        ecu_b.stop()
        victim.stop()
        attacker.stop()
        master.stop()


if __name__ == "__main__":
    main()
