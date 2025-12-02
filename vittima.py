import can
import time
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

# Variabili di stato globale
victim_tec_sim = INITIAL_TEC
attack_active = False # Flag: True se l'attacco è stato rilevato
tx_message_counter = 0

def update_tec(current_tec):
    """
    Calcola il nuovo TEC della Vittima in base alla fase dell'attacco.
    (Fase 1: +8, Fase 2: +7).
    """
    if current_tec < TEC_PASSIVE_THRESHOLD:
        # Fase 1: Error Active -> Aumento di +8
        return current_tec + 8, 8, "Active"
    else:
        # Fase 2: Error Passive -> Aumento di +7 (Netto +8 -1)
        return current_tec + 7, 7, "Passive"

def start_victim_final():
    global victim_tec_sim, attack_active, tx_message_counter
    
    try:
        # receive_own_messages=False è CRUCIALE per evitare che la Vittima riceva l'eco di sé stessa.
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=False)
        print(f"✅ [Vittima] Connessa a {CAN_INTERFACE}. TEC Iniziale: {victim_tec_sim}")
    except OSError as e:
        print(f"❌ [Vittima] Errore di connessione: {e}")
        return

    start_time = time.time()
    
    while True:
        
        # 1. CHECK AUTO-TERMINAZIONE
        if victim_tec_sim >= BUS_OFF_THRESHOLD:
            print(f"\n🚨🚨 [Vittima] BUS OFF RILEVATO! (TEC Sim: {victim_tec_sim}). Auto-terminazione.")
            break
        
        # 2. Ciclo di Trasmissione
        if (time.time() - start_time) >= TRANSMISSION_PERIOD_SEC:
            
            print(f"\n--- CICLO VITTIMA #{tx_message_counter+1} ({time.strftime('%H:%M:%S')}) ---")
            print(f"✅ [Vittima] Bus Pulito. TEC Sim Precedente: {victim_tec_sim}") # Stampa il TEC PRECEDENTE
            
            # 3. Tentativo di Invio (Simulazione Bit Monitoring)
            try:
                # Usa un payload randomico per differenziarsi da qualsiasi payload fisso dell'Attaccante.
                data_payload = [random.randint(0, 255) for _ in range(8)]
                msg_tx = can.Message(
                    arbitration_id=TARGET_ID,
                    data=data_payload,
                    is_extended_id=False
                )
                bus.send(msg_tx)
                print(f"🚀 [Vittima] Messaggio inviato (ID: {hex(TARGET_ID)}).")
                
                # 4. ASCOLTO IMMEDIATO PER RILEVARE L'ATTACCANTE
                # VCAN aspetta un istante (timeout=0.01) per vedere se un altro nodo invia
                # un messaggio con lo stesso ID (l'Attaccante).
                attack_msg = bus.recv(timeout=0.01) 
                
                # 5. AGGIORNAMENTO STATO ATTACCO
                if attack_msg is not None and attack_msg.arbitration_id == TARGET_ID:
                    # Se riceviamo un messaggio con TARGET_ID subito dopo l'invio,
                    # è l'Attaccante che sta creando il conflitto (Bit Error).
                    attack_active = True
                    print("🔥 ATTACCO RILEVATO: Rilevato messaggio in conflitto subito dopo la trasmissione.")
                
                # 6. AGGIORNAMENTO CRITICO DEL TEC (Fine Ciclo)
                if attack_active:
                    victim_tec_sim, tec_change, status = update_tec(victim_tec_sim)
                    print(f"⚠️ [Vittima] Errore registrato. TEC Sim ATTUALE: {victim_tec_sim} ({tec_change:+d}) Stato: {status}")

                tx_message_counter += 1
                start_time = time.time()
            
            except Exception as e:
                print(f"❌ [Vittima] Errore in trasmissione o ricezione: {e}")
                break
        
        time.sleep(0.01)

    bus.shutdown()
    print("\n🛑 [Vittima] Disconnessa.")

if __name__ == '__main__':
    start_victim_final()
