import can
import time
import threading
import sys

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
TRANSMISSION_PERIOD_SEC = 5.0
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128
INITIAL_TEC = 0
# ----------------------

# Variabili condivise per il TEC SIMULATO della Vittima
victim_tec_sim = INITIAL_TEC
attack_active = threading.Event() # Flag: L'errore è stato rilevato

def update_tec(current_tec):
    """Calcola il nuovo TEC della Vittima in base alla fase dell'attacco."""
    # La Vittima non sa se l'attaccante è fermo, quindi continua ad aumentare il TEC.
    if current_tec < TEC_PASSIVE_THRESHOLD:
        # Fase 1: Error Active -> Aumento di +8
        return current_tec + 8, 8, "Active"
    else:
        # Fase 2: Error Passive -> Aumento di +7 (Netto +8 -1)
        return current_tec + 7, 7, "Passive"

def start_victim_reactive():
    global victim_tec_sim, attack_active
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=True)
        print(f"✅ [Vittima] Connessa a {CAN_INTERFACE}. TEC Iniziale: {victim_tec_sim}")
    except OSError as e:
        print(f"❌ [Vittima] Errore di connessione: {e}")
        return

    message_counter = 0
    start_time = time.time()
    
    # Listener per rilevare l'inizio dell'attacco (ovvero il conflitto ID)
    listener_thread = threading.Thread(target=sniff_for_attack_start, args=(bus,))
    listener_thread.daemon = True
    listener_thread.start()

    while True:
        
        # 1. CHECK AUTO-TERMINAZIONE (Bus Off simulato)
        if victim_tec_sim >= BUS_OFF_THRESHOLD:
            print(f"\n🚨🚨 [Vittima] BUS OFF RILEVATO! (TEC Sim: {victim_tec_sim}). Auto-terminazione.")
            break
        
        # 2. Ciclo di Trasmissione (solo se è tempo)
        if (time.time() - start_time) >= TRANSMISSION_PERIOD_SEC:
            
            print(f"\n--- CICLO VITTIMA #{message_counter+1} ({time.strftime('%H:%M:%S')}) ---")
            
            # 3. AUTO-RILEVAZIONE DELL'ERRORE E AGGIORNAMENTO TEC
            if attack_active.is_set():
                # Il conflitto è stato rilevato, quindi il TEC aumenta in ogni ciclo di trasmissione
                victim_tec_sim, tec_change, status = update_tec(victim_tec_sim)
                print(f"⚠️ [Vittima] Conflitto Dominante Rilevato! TEC Sim: {victim_tec_sim} ({tec_change:+d}) Stato: {status}")
            else:
                print(f"✅ [Vittima] Bus Pulito. TEC Sim: {victim_tec_sim}")

            # 4. Invio
            try:
                msg_tx = can.Message(
                    arbitration_id=TARGET_ID,
                    data=[message_counter % 256, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00],
                    is_extended_id=False
                )
                bus.send(msg_tx)
                print(f"🚀 [Vittima] Messaggio inviato (ID: {hex(TARGET_ID)}). In attesa di {TRANSMISSION_PERIOD_SEC}s...")
                message_counter += 1
                start_time = time.time()
            
            except Exception:
                break
        
        time.sleep(0.01)

    bus.shutdown()
    print("\n🛑 [Vittima] Disconnessa.")

def sniff_for_attack_start(bus):
    global attack_active
    print(f"👂 [Vittima Listener] Monitoraggio per messaggi con ID {hex(TARGET_ID)} (Conflitto)...")
    
    # *** NUOVA VARIABILE DI STATO ***
    own_message_sent = False
    
    while not attack_active.is_set():
        msg = bus.recv(timeout=None) 
        
        if msg is not None and msg.arbitration_id == TARGET_ID and msg.is_error_frame == False:
            
            if not own_message_sent:
                # Questo è il primo messaggio, assumiamo sia il messaggio della Vittima stessa.
                # Lo impostiamo a True e lo ignoriamo.
                own_message_sent = True
                print(f"✅ [Vittima Listener] Rilevato il proprio primo messaggio. In attesa dell'Attaccante...")
                continue # Salta il resto del ciclo e aspetta il messaggio successivo
            
            else:
                # Se own_message_sent è True e riceviamo ANCORA un TARGET_ID, 
                # significa che l'Attaccante è partito.
                print(f"🔥 [Vittima Listener] RILEVATO MESSAGGIO CON ID CONFLITTUALE. ATTACCO ATTIVO.")
                attack_active.set() 
                return
        
if __name__ == '__main__':
    start_victim_reactive()
