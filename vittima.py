import can
import time

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123
KILL_ID = 0x777  # ID speciale per la terminazione
TRANSMISSION_PERIOD_SEC = 5.0
# ----------------------

def start_victim_receiving():
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=True)
        print(f"✅ [Vittima] Connessa a {CAN_INTERFACE}. In attesa di segnale KILL: {hex(KILL_ID)}")
    except OSError as e:
        print(f"❌ [Vittima] Errore di connessione: {e}")
        return

    message_counter = 0
    start_time = time.time()

    while True:
        # 1. RICEZIONE/CHECK SEGNALE DI TERMINAZIONE
        # Controlla velocemente se ci sono messaggi dall'Attaccante
        msg = bus.recv(timeout=0.01) 
        if msg is not None and msg.arbitration_id == KILL_ID:
            print(f"\n🚨🚨 [Vittima] SEGNALE KILL RICEVUTO ({hex(KILL_ID)}). Terminazione forzata.")
            break

        # 2. Ciclo di Trasmissione (solo se è tempo)
        if (time.time() - start_time) >= TRANSMISSION_PERIOD_SEC:
            
            print(f"\n--- CICLO VITTIMA #{message_counter+1} ({time.strftime('%H:%M:%S')}) ---")
            
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
            
            except can.CanError as e:
                print(f"⚠️ [Vittima] Errore di trasmissione CAN: {e}. Interruzione.")
                break 
            except OSError as e:
                print(f"❌ [Vittima] Errore di sistema: {e}. Interruzione.")
                break
        
        # Mantiene il ciclo attivo per il check del timeout
        time.sleep(0.01)

    bus.shutdown()
    print("\n🛑 [Vittima] Disconnessa.")

if __name__ == '__main__':
    start_victim_receiving()
