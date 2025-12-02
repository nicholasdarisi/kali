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

# Variabili condivise
victim_tec_sim = INITIAL_TEC
attack_active = threading.Event() 
# Contatore globale che tiene traccia di quanti messaggi la Vittima HA INVIATO.
# Il listener userà questo per distinguere i messaggi propri da quelli estranei.
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
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=True)
        print(f"✅ [Vittima] Connessa a {CAN_INTERFACE}. TEC Iniziale: {victim_tec_sim}")
    except OSError as e:
        print(f"❌ [Vittima] Errore di connessione: {e}")
        return

    start_time = time.time()
    
    # Avvia il listener
    listener_thread = threading.Thread(target=sniff_for_attack_start, args=(bus,))
    listener_thread.daemon = True
    listener_thread.start()

    while True:
        
        if victim_tec_sim >= BUS_OFF_THRESHOLD:
            print(f"\n🚨🚨 [Vittima] BUS OFF RILEVATO! (TEC Sim: {victim_tec_sim}). Auto-terminazione.")
            break
        
        if (time.time() - start_time) >= TRANSMISSION_PERIOD_SEC:
            
            # 1. RILEVAZIONE ERRORE E AGGIORNAMENTO TEC
            print(f"\n--- CICLO VITTIMA #{tx_message_counter+1} ({time.strftime('%H:%M:%S')}) ---")
            
            if attack_active.is_set():
                # Il conflitto è attivo: aumenta il TEC
                victim_tec_sim, tec_change, status = update_tec(victim_tec_sim)
                print(f"⚠️ [Vittima] Conflitto Dominante Rilevato! TEC Sim: {victim_tec_sim} ({tec_change:+d}) Stato: {status}")
            else:
                # Nessun attacco rilevato: TEC invariato
                print(f"✅ [Vittima] Bus Pulito. TEC Sim: {victim_tec_sim}")

            # 2. Invio e Aggiornamento Contatore
            try:
                msg_tx = can.Message(
                    arbitration_id=TARGET_ID,
                    data=[tx_message_counter % 256, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00],
                    is_extended_id=False
                )
                bus.send(msg_tx)
                print(f"🚀 [Vittima] Messaggio inviato (ID: {hex(TARGET_ID)}). In attesa di {TRANSMISSION_PERIOD_SEC}s...")
                
                # *** AGGIORNAMENTO CRITICO DEL CONTATORE ***
                tx_message_counter += 1 
                start_time = time.time()
            
            except Exception:
                break
        
        time.sleep(0.01)

    bus.shutdown()
    print("\n🛑 [Vittima] Disconnessa.")

def sniff_for_attack_start(bus):
    """
    Simula la rilevazione implicita dell'errore. Si attiva solo se un messaggio con TARGET_ID
    viene ricevuto quando la Vittima NON si aspetta il proprio messaggio (ovvero è l'Attaccante).
    """
    global attack_active, tx_message_counter
    print(f"👂 [Vittima Listener] Monitoraggio per conflitti (ID: {hex(TARGET_ID)})...")
    
    while not attack_active.is_set():
        # Legge tutti i messaggi che arrivano
        msg = bus.recv(timeout=None) 
        
        if msg is not None and msg.arbitration_id == TARGET_ID and msg.is_error_frame == False:
            
            # Se la Vittima non ha ancora inviato questo numero di messaggi, è il suo stesso messaggio.
            # Il campo dati contiene il tx_message_counter nel primo byte.
            # Se il contatore ricevuto nel messaggio (msg.data[0]) è maggiore o uguale
            # al numero di messaggi che la Vittima ha finito di inviare (tx_message_counter),
            # è un messaggio interno che stiamo monitorando.
            
            # Se il primo byte del messaggio ricevuto NON è l'indice del messaggio che
            # la Vittima ha appena inviato, è un messaggio estraneo (l'Attaccante).
            
            # Nota: Questa è una potente euristica nella simulazione, assumendo che solo la Vittima
            # aggiorni questo byte e che l'Attaccante mandi payload non sincronizzati.
            
            # Il contatore nel messaggio ricevuto dovrebbe essere uguale a tx_message_counter - 1 (se la Vittima è veloce)
            # o uguale a tx_message_counter (se il thread riceve prima dell'aggiornamento del contatore).
            
            # Semplicemente: se il messaggio NON contiene il contatore dell'ultimo messaggio inviato, è l'attaccante.
            # Qui si usa una logica più diretta: Se il contatore ricevuto è 0, e noi ne abbiamo già inviati, è un attacco.
            
            if msg.data[0] != (tx_message_counter - 1) % 256 and tx_message_counter > 0:
                 # Il messaggio ricevuto ha un payload [0x00, ...] e la Vittima ha un contatore > 0.
                 # Il messaggio dell'Attaccante (payload tutti zeri) differisce dal payload della Vittima.
                 # Questo è il segnale che stiamo cercando.
                 print(f"🔥 [Vittima Listener] RILEVATO MESSAGGIO ESTRANEO/CONFLITTUALE. ATTACCO ATTIVO.")
                 attack_active.set() 
                 return 
        
if __name__ == '__main__':
    start_victim_corrected()
