"""
CAN BUS Simulator - VERSIONE MODIFICATA (Fix Bus Off)
Modifiche:
1. Aggiunto metodo inject_error_frame nel Master.
2. Il Master ora interrompe la trasmissione e svuota la coda su errore.
"""

import time
import threading
import queue
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional

# Tenta l'import di python-can, se fallisce disabilita socketCAN
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
    is_attacker: bool = False
    is_victim: bool = False


@dataclass
class BitTransmission:
    bit_value: BitValue
    timestamp: float
    sender_name: str
    logical_source: str  # 'VICTIM', 'ATTACKER', 'ECU', 'ERROR_FLAG'


class CANMaster:
    def __init__(self, tick_ms: float = 0.5, forward_to_socketcan: bool = True, can_channel: str = "vcan0"):
        self.tick = tick_ms / 1000.0
        self.state = MasterState.IDLE
        self.requests_queue = queue.PriorityQueue()  # (priority, TransmissionRequest)
        self.current_req: Optional[TransmissionRequest] = None
        
        # Coda dei bit fisici che il master deve "scrivere" sul bus
        self.current_bits = queue.Queue()
        
        self.slaves: Dict[int, 'BaseECU'] = {}
        self.running = False
        self.lock = threading.Lock()
        
        # SocketCAN init
        self.forward_to_socketcan = forward_to_socketcan and CAN_AVAILABLE
        self.bus = None
        if self.forward_to_socketcan:
            try:
                self.bus = can.interface.Bus(channel=can_channel, bustype='socketcan')
                print(f"[MASTER] Collegato a socketCAN su {can_channel}")
            except Exception as e:
                print(f"[MASTER] Errore connessione socketCAN: {e}")
                self.forward_to_socketcan = False

    def start(self):
        self.running = True
        t = threading.Thread(target=self._master_loop, daemon=True)
        t.start()
        print("[MASTER] Avvio master loop")

    def register_slave(self, slave: 'BaseECU'):
        with self.lock:
            self.slaves[slave.slave_id] = slave
            print(f"[MASTER] Registrata ECU {slave.name} (slave_id={slave.slave_id}, ID={hex(slave.arbitration_id)})")

    def request_tx(self, req: TransmissionRequest):
        # Priorità basata su arbitration_id (più basso = priorità alta)
        self.requests_queue.put((req.arbitration_id, req))
        # print(f"[MASTER] Ricevuta richiesta TX da {req.slave_name} (ID={hex(req.arbitration_id)})")

    # ---------------------------------------------------------
    # NUOVO METODO: Gestione Error Frame
    # ---------------------------------------------------------
    def inject_error_frame(self):
        """
        Interrompe immediatamente la trasmissione corrente, svuota la coda
        e inserisce 6 bit DOMINANT (Error Flag) per simulare la distruzione del frame.
        """
        with self.lock:
            # Se non stiamo trasmettendo nulla di importante, ignoriamo
            if self.current_bits.empty() and self.state == MasterState.IDLE:
                return

            print(f"[MASTER] ⚠️  Rilevato ERRORE: INIEZIONE ERROR FRAME (Abort TX)")
            
            # 1. SVUOTA LA CODA: Cancella i bit restanti del pacchetto originale (impedisce il successo)
            with self.current_bits.mutex:
                self.current_bits.queue.clear()

            # 2. INSERISCE ERROR FLAG: 6 bit DOMINANT
            now = time.time()
            for i in range(6):
                error_bit = BitTransmission(
                    bit_value=BitValue.DOMINANT,
                    timestamp=now + (i * self.tick),
                    sender_name="MASTER_ERR",
                    logical_source="ERROR_FLAG"
                )
                self.current_bits.put(error_bit)
            
            # 3. INSERISCE ERROR DELIMITER: 8 bit RECESSIVE (per pulire il bus)
            for i in range(8):
                delim_bit = BitTransmission(
                    bit_value=BitValue.RECESSIVE,
                    timestamp=now + ((6+i) * self.tick),
                    sender_name="MASTER_ERR",
                    logical_source="ERROR_DELIM"
                )
                self.current_bits.put(delim_bit)
            
            # Opzionale: Resettiamo lo stato del master
            # self.state = MasterState.IDLE (lo farà il loop quando finisce i bit)

    def notify_error(self, node_state):
        """
        Chiamato da una ECU quando rileva un errore di bit.
        """
        # Invece di loggare e basta, ora agiamo fisicamente sul bus
        self.inject_error_frame()

    def _master_loop(self):
        while self.running:
            # 1. Se stiamo trasmettendo bit fisici (il frame o un error frame)
            if not self.current_bits.empty():
                self._process_bits()
            else:
                # 2. Se non stiamo trasmettendo, controlliamo se il frame è finito
                if self.state == MasterState.TRANSMIT:
                    print(f"[MASTER] Coda bit vuota → passo a EOF")
                    self.state = MasterState.EOF
                    
                    # Se siamo arrivati qui senza errori (coda svuotata naturalmente), è un successo
                    if self.current_req:
                        print(f"[MASTER] EOF: frame di {self.current_req.slave_name} considerato OK → inoltro data frame su socketCAN")
                        if self.forward_to_socketcan and self.bus:
                            try:
                                msg = can.Message(arbitration_id=self.current_req.arbitration_id, 
                                                  data=self.current_req.data, 
                                                  is_extended_id=False)
                                self.bus.send(msg)
                            except Exception as e:
                                print(f"[MASTER] Errore invio socketCAN: {e}")
                    
                    self.current_req = None
                    self.state = MasterState.IDLE
                    time.sleep(self.tick * 3)  # Interframe space simulato

                # 3. Arbitraggio: chi vince?
                self._arbitrate()
            
            time.sleep(self.tick)

    def _process_bits(self):
        try:
            bit_obj = self.current_bits.get(block=False)
            
            # Simuliamo la propagazione a tutte le ECU
            # Nota: qui semplifichiamo. In realtà ogni ECU campiona il bus.
            # Qui diciamo alle ECU: "Il bus ora è a questo valore".
            
            val_str = "DOMINANT" if bit_obj.bit_value == BitValue.DOMINANT else "RECESSIVE"
            # print(f"[MASTER] TX bit: {val_str} (orig: {bit_obj.logical_source})")
            
            for s_id, slave in self.slaves.items():
                slave.read_bus(bit_obj)
                
        except queue.Empty:
            pass

    def _arbitrate(self):
        if self.requests_queue.empty():
            return

        # Prende tutte le richieste pendenti
        candidates = []
        while not self.requests_queue.empty():
            candidates.append(self.requests_queue.get())
        
        print(f"[MASTER] IDLE: {len(candidates)} richieste di TX da gestire")

        # Logica semplice: vince chi ha ID più basso (standard CAN)
        # La PriorityQueue lo fa già in parte, ma gestiamo conflitti
        winner = candidates[0]
        
        # Rimettiamo le altre in coda (non vincenti)
        for c in candidates[1:]:
            self.requests_queue.put((c.arbitration_id, c))
        
        print(f"[MASTER] Nessun arbitraggio complesso implementato: trasmetto {winner.slave_name}")
        self.current_req = winner
        self.state = MasterState.TRANSMIT
        
        # Generiamo i bit per questo frame e li mettiamo in current_bits
        self._prepare_bits_for_current_req()

    def _prepare_bits_for_current_req(self):
        if not self.current_req:
            return
        
        print(f"[MASTER] Preparo bit per {self.current_req.slave_name}")
        # SOF (1 bit DOMINANT)
        bits = [BitValue.DOMINANT]
        
        # Arbitration ID (11 bit)
        arb_id = self.current_req.arbitration_id
        for i in range(10, -1, -1):
            bit = (arb_id >> i) & 1
            bits.append(BitValue.RECESSIVE if bit == 1 else BitValue.DOMINANT)
        
        # RTR (1 bit DOMINANT per Data Frame)
        bits.append(BitValue.DOMINANT)
        
        # IDE (1 bit DOMINANT per Standard Frame)
        bits.append(BitValue.DOMINANT)
        
        # Reserved r0 (1 bit DOMINANT solitamente, ma RECESSIVE in alcuni standard vecchi o estesi)
        # Standard CAN 2.0A: r0 è riservato. Mettiamolo RECESSIVE per dare spazio all'attaccante di vederlo.
        # Nello standard moderno è Dominant, ma facciamo Recessive per facilitare l'attacco di esempio
        bits.append(BitValue.RECESSIVE) 
        
        # DLC (4 bit)
        dlc = len(self.current_req.data)
        for i in range(3, -1, -1):
            bit = (dlc >> i) & 1
            bits.append(BitValue.RECESSIVE if bit == 1 else BitValue.DOMINANT)
            
        # Data Field
        for byte in self.current_req.data:
            for i in range(7, -1, -1):
                bit = (byte >> i) & 1
                bits.append(BitValue.RECESSIVE if bit == 1 else BitValue.DOMINANT)
                
        # CRC (15 bit) - Calcolo finto/semplice
        crc = self._calculate_crc(self.current_req.data)
        for i in range(14, -1, -1):
            bit = (crc >> i) & 1
            bits.append(BitValue.RECESSIVE if bit == 1 else BitValue.DOMINANT)
            
        # CRC Delimiter (1 bit RECESSIVE)
        bits.append(BitValue.RECESSIVE)
        
        # ACK Slot (1 bit RECESSIVE - scritto dal trasmittente, sovrascritto da altri)
        bits.append(BitValue.RECESSIVE)
        
        # ACK Delimiter (1 bit RECESSIVE)
        bits.append(BitValue.RECESSIVE)
        
        # EOF (7 bit RECESSIVE)
        for _ in range(7):
            bits.append(BitValue.RECESSIVE)
            
        # Popola la coda fisica
        now = time.time()
        count = 0
        for b_val in bits:
            bt = BitTransmission(
                bit_value=b_val,
                timestamp=now + (count * self.tick),
                sender_name=self.current_req.slave_name,
                logical_source="VICTIM" if self.current_req.is_victim else "ECU"
            )
            self.current_bits.put(bt)
            count += 1
            
        print(f"[MASTER] Bit preparati: coda ha {self.current_bits.qsize()} elementi")


    def _calculate_crc(self, data: bytes) -> int:
        # Fake CRC-15
        return 0x4599 # Valore a caso


class BaseECU:
    def __init__(self, name: str, slave_id: int, arbitration_id: int, master: CANMaster, interval: float, is_victim: bool = False):
        self.name = name
        self.slave_id = slave_id
        self.arbitration_id = arbitration_id
        self.master = master
        self.interval = interval
        self.is_victim = is_victim
        
        self.running = False
        self.tec = 0  # Transmit Error Counter
        self.rec = 0  # Receive Error Counter
        self.state = NodeState.ERROR_ACTIVE
        
        # Attacco
        self.attack_active = False # Solo per attaccante
        
        # Sincronizzazione bit
        self.current_bit_idx = 0
        
        self.master.register_slave(self)

    def start(self):
        self.running = True
        t = threading.Thread(target=self._ecu_loop, daemon=True)
        t.start()
        print(f"[{self.name}] Avvio ECU (ID={hex(self.arbitration_id)}, victim={self.is_victim})")

    def _ecu_loop(self):
        # Loop per generare messaggi
        while self.running:
            if self.state == NodeState.BUS_OFF:
                print(f"[{self.name}] BUS OFF! Non trasmetto più.")
                time.sleep(5) # Recovery time simulato
                # self.tec = 0
                # self.state = NodeState.ERROR_ACTIVE
                # print(f"[{self.name}] Recovery da BUS OFF.")
                continue

            time.sleep(self.interval + random.uniform(0, 0.5))
            
            # Se siamo l'attaccante, non generiamo messaggi normali, aspettiamo solo di attaccare
            if self.name == "ATTACKER":
                continue
                
            self.request_tx()

    def request_tx(self):
        if self.state == NodeState.BUS_OFF:
            return

        # Dati a caso
        data = bytes([random.randint(0, 255) for _ in range(8)])
        print(f"[{self.name}] Richiedo TX data={data.hex().upper()} (state={self.state.name}, TEC={self.tec})")
        
        req = TransmissionRequest(
            slave_name=self.name,
            slave_id=self.slave_id,
            arbitration_id=self.arbitration_id,
            data=data,
            timestamp=time.time(),
            is_victim=self.is_victim
        )
        self.master.request_tx(req)

    def read_bus(self, bit_obj: BitTransmission):
        """
        Chiamato dal Master per ogni bit trasmesso sul bus.
        """
        # Logica semplificata di ricezione/attacco
        self._monitor_bus(bit_obj)

    def _monitor_bus(self, bit_obj: BitTransmission):
        # ----------------------------------------------------
        # LOGICA ATTACCANTE
        # ----------------------------------------------------
        if self.name == "ATTACKER":
            # L'attaccante spia. Cerca l'ID della vittima (0x123)
            # Semplificazione: contiamo i bit e sappiamo la struttura del frame
            # ID: bit 1..11. r0: bit 14.
            
            # Se inizia un nuovo frame (SOF dominant dopo idle/interframe)
            # Qui usiamo un contatore grezzo resettato dal master implicitly (non ideale ma funge per la demo)
            pass 
            
            # ATTACCO SPECIFICO:
            # Se il bit in arrivo è quello 'r0' del frame della vittima ed è RECESSIVE,
            # l'attaccante lo forza a DOMINANT.
            
            # Come sappiamo che è r0? Nel simulatore semplice, contiamo i bit dall'inizio del pacchetto se l'ID corrisponde.
            # O più semplicemente: guardiamo bit_obj.logical_source
            
            if bit_obj.logical_source == "VICTIM":
                # Siamo sincronizzati sul frame della vittima
                # Nella struttura CAN standard/extended, r0 è circa il 13-14esimo bit
                # SOF(1) + ID(11) + RTR(1) + IDE(1) + r0(1) = 15esimo bit (indice 14)
                # Ma non abbiamo contatore qui...
                
                # TRUCCO PER DEMO: attacchiamo se vediamo un RECESSIVE e decidiamo che è il momento
                # Per essere precisi dovremmo implementare una macchina a stati RX completa.
                # Qui usiamo un hack: attacchiamo se il master dice che è il bit r0 (lo sappiamo dall'indice se avessimo accesso)
                # O per semplicità: attacchiamo SEMPRE se il frame è della vittima e vediamo un recessive nella zona di controllo.
                
                pass

        # ----------------------------------------------------
        # LOGICA GENERALE DI RICEZIONE E CONTROLLO ERRORE
        # ----------------------------------------------------
        
        # Per la demo, implementiamo la logica di attacco DIRECT INJECTION qui
        # L'attaccante "sovrascrive" il valore nel master se vince l'arbitraggio fisico.
        # Ma qui siamo in lettura.
        
        # Modifica sporca per simulare l'attacco REAL TIME:
        if self.name == "ATTACKER" and bit_obj.logical_source == "VICTIM":
            # Indice bit (non passato dal master, ma possiamo stimarlo o hackerarlo)
            # Supponiamo di voler attaccare il bit r0. 
            # Nel _prepare_bits, r0 è circa al 14esimo posto.
            
            # Simuliamo l'attacco su un bit specifico se è RECESSIVE
            # (Nel loggy2 vediamo che r0 è RECESSIVE e l'attaccante lo vuole DOMINANT)
            
            # NOTA: In questo simulatore python single-thread, non possiamo "sovrascrivere" il bit corrente
            # prima che gli altri lo leggano, a meno che non interveniamo sulla queue del master O se il master
            # gestisce la collisione.
            
            # Simuliamo che l'attaccante abbia AGITO.
            # Se bit_obj.bit_value è RECESSIVE e noi spariamo DOMINANT -> Bit Error per la vittima.
            
            # Hack: Contiamo i bit ricevuti consecutivi da "VICTIM"
            if not hasattr(self, 'victim_bit_count'): self.victim_bit_count = 0
            
            self.victim_bit_count += 1
            
            # r0 è il 14esimo bit (index 13) se partiamo da 0.
            # SOF(1), ID(11), RTR(1), IDE(1) -> 14 bit. Il prossimo è r0.
            if self.victim_bit_count == 15: # Circa qui
                if bit_obj.bit_value == BitValue.RECESSIVE:
                    print(f"[ATTACKER] FORZA r0=DOMINANT (attacco)")
                    # Cambiamo il valore "al volo" per simulare il bus fisico dominato
                    bit_obj.bit_value = BitValue.DOMINANT
                    bit_obj.sender_name = "ATTACKER" # L'attaccante vince
        else:
            if hasattr(self, 'victim_bit_count') and bit_obj.logical_source != "VICTIM":
                self.victim_bit_count = 0

        # ----------------------------------------------------
        # LOGICA VITTIMA: VERIFICA DI QUELLO CHE LEGGE
        # ----------------------------------------------------
        if self.is_victim:
            # La vittima legge il bus. Se stava trasmettendo RECESSIVE e legge DOMINANT -> Bit Error
            # (A meno che non sia in arbitration field o ACK slot)
            
            # Stiamo trasmettendo noi?
            is_my_tx = (bit_obj.logical_source == "VICTIM" or bit_obj.sender_name == self.name)
            
            if is_my_tx:
                # Controlliamo coerenza (molto semplificata)
                # Sappiamo che nel _prepare_bits, r0 è stato messo RECESSIVE per la vittima.
                # Se ora leggiamo DOMINANT (a causa dell'attaccante), è un errore.
                
                # Per rilevare l'errore specifico r0 senza macchina a stati complessa:
                if bit_obj.sender_name == "ATTACKER":
                    print(f"[{self.name}] 💥 BIT ERROR r0! Expected RECESSIVE, actual DOMINANT")
                    self._on_tx_error()
                    # NOTIFICA IL MASTER DELL'ERRORE -> QUESTO CAUSERA' L'INIEZIONE DELL'ERROR FRAME
                    self.master.notify_error(self.state)
                    
                    # Reset contatori interni
                    bit_count = 0

    def _on_tx_error(self):
        increment = 8 if self.state == NodeState.ERROR_ACTIVE else 8 
        # Nota: anche in Passive aumenta di 8, ma non può mandare Active Flag.
        self.tec += increment
        self._update_state()
        print(f"[{self.name}] ❌ TEC+8 → {self.tec} ({self.state.name})")

    def _update_state(self):
        if self.tec > 255:
            self.state = NodeState.BUS_OFF
        elif self.tec > 127:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE


def main():
    print("CAN BUS ATTACK SIMULATOR - FIX BUS OFF")
    master = CANMaster(tick_ms=0.1, forward_to_socketcan=True)
    
    # ECU normali per arbitraggio
    ecu_a = BaseECU("ECU_A", 1, 0x100, master, 3.0)
    ecu_b = BaseECU("ECU_B", 2, 0x200, master, 3.0)
    
    # Vittima e Attaccante
    victim = BaseECU("VICTIM", 10, 0x123, master, 2.0, is_victim=True)
    attacker = BaseECU("ATTACKER", 11, 0x123, master, 2.0)
    
    master.start()
    ecu_a.start()
    ecu_b.start()
    victim.start()
    attacker.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stop.")

if __name__ == "__main__":
    main()
