import can
import time
import threading
import sys
import random

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
TRANSMISSION_PERIOD_SEC = 5.0
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128
INITIAL_TEC = 0
# ----------------------

# Variabili condivise
victim_tec_sim = INITIAL_TEC
attack_active = False # NON è più un evento, è un semplice flag boolean
tx_message_counter = 0

def update_tec(current_tec):
    """Calcola il nuovo TEC della Vittima in base alla fase dell'attacco."""
    if current_tec < TEC_PASSIVE_THRESHOLD:
        return current_tec + 8, 8, "Active"
    else:
        return current_tec + 7, 7, "Passive"

def start_victim_corrected():
    global victim_tec_sim, attack_active, tx_message_counter
    
    try:
        # receive_own_messages=False aiuta a minimizzare l'eco immediata
        # ma l'Attaccante deve comunque forzare il conflitto.
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=False)
        print(f"✅ [Vittima] Connessa a {CAN_INTERFACE}. TEC Iniziale: {victim_tec_sim}")
    except OSError as e:
        print(f"❌ [Vittima] Errore di connessione: {e}")
        return

    start_time = time.time()
    
    while True:
        
        if victim_tec_sim >= BUS_OFF_THRESHOLD:
            print(f"\n🚨🚨 [Vittima] BUS OFF RILEVATO! (TEC Sim: {victim_tec_sim}). Auto-terminazione.")
            break
        
        # 1. Ciclo di Trasmissione
        if (time.time() - start_time) >= TRANSMISSION_PERIOD_SEC:
            
            print(f"\n--- CICLO VITTIMA #{tx_message_counter+1} ({time.strftime('%H:%M:%S')}) ---")
            
            # 2. RILEVAZIONE ERRORE E AGGIORNAMENTO TEC (prima di inviare il messaggio)
            if attack_active:
                victim_tec_sim, tec_change, status = update_tec(victim_tec_sim)
                print(f"⚠️ [Vittima] Conflitto Dominante Rilevato! TEC Sim: {victim_tec_sim} ({tec_change:+d}) Stato: {status}")
            else:
                print(f"✅ [Vittima] Bus Pulito. TEC Sim: {victim_tec_sim}")

            # 3. Tentativo di Invio
            try:
                # Usiamo un payload non sequenziale per non fare affidamento sulla sequenza dell'Attaccante
                data_payload = [random.randint(0, 255) for _ in range(8)]
                msg_tx = can.Message(
                    arbitration_id=TARGET_ID,
                    data=data_payload,
                    is_extended_id=False
                )
                bus.send(msg_tx)
                print(f"🚀 [Vittima] Messaggio inviato (ID: {hex(TARGET_ID)}).")
                
                # 4. **ASCOLTO IMMEDIATO PER RILEVARE L'ATTACCANTE**
                # Se l'Attaccante è attivo, sta inviando il suo messaggio DOMINANTE in questo momento.
                # L'Attaccante non ha un timer, aspetta solo di ricevere.

                # Il timeout è breve, solo per catturare l'eventuale messaggio dell'Attaccante
                # che sta causando il Bit Error sul bus.
                attack_msg = bus.recv(timeout=0.01) 
                
                if attack_msg is not None and attack_msg.arbitration_id == TARGET_ID:
                    # Rilevato il messaggio dell'Attaccante subito dopo l'invio della Vittima
                    # Questa è la nostra condizione di sincronizzazione e attivazione dell'attacco.
                    attack_active = True
                    print("🔥 ATTACCO RILEVATO: Rilevato messaggio in conflitto subito dopo la trasmissione.")
                
                tx_message_counter += 1
                start_time = time.time()
            
            except Exception:
                break
        
        time.sleep(0.01)

    bus.shutdown()
    print("\n🛑 [Vittima] Disconnessa.")

if __name__ == '__main__':
    start_victim_corrected()
