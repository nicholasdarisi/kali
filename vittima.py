import can
import time
import subprocess
import re

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123
TRANSMISSION_PERIOD_SEC = 5.0
BUS_OFF_THRESHOLD = 256
# ----------------------

def get_tec_info(interface):
    """
    Legge il valore di TEC (Transmit Error Counter) e lo stato del bus dal kernel.
    """
    try:
        command = ['ip', '-details', 'link', 'show', interface]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        
        tec_match = re.search(r'tec\s+(\d+)\s+rec\s+(\d+)', output)
        # Cerca lo stato come BUS-OFF, ERROR-PASSIVE, ecc.
        state_match = re.search(r'state\s+(\S+)', output) 

        tec_value = int(tec_match.group(1)) if tec_match else -1
        # Usiamo solo la prima parte dello stato (es: da 'BUS-OFF' a 'BUS')
        state = state_match.group(1).split('-')[0] if state_match else "UNKNOWN"
        
        return tec_value, state
            
    except Exception as e:
        # Errore, ad esempio se l'interfaccia non esiste o 'ip' fallisce.
        return -2, "ERROR"

def start_victim():
    """Simula la vittima che trasmette e monitora il suo TEC reale."""
    
    try:
        # Aggiungo receive_own_messages=True per garantire che il nodo si veda sul bus
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan', receive_own_messages=True)
        print(f"✅ [Vittima] Connessa a {CAN_INTERFACE}. ID bersaglio: {hex(TARGET_ID)}")
    except OSError as e:
        print(f"❌ [Vittima] Errore di connessione a {CAN_INTERFACE}: {e}")
        return

    message_counter = 0

    while True:
        # 1. MONITORAGGIO TEC REALE E STATO
        tec_real, status_real = get_tec_info(CAN_INTERFACE)

        print(f"\n--- CICLO VITTIMA #{message_counter+1} ({time.strftime('%H:%M:%S')}) ---")
        print(f"🔬 [Vittima] TEC REALE: {tec_real}. Stato Kernel: {status_real}")

        # 2. CONTROLLO BUS OFF
        if status_real == "BUS": # Rileva BUS-OFF
            print(f"🚨🚨 [Vittima] RILEVATO STATO **BUS OFF** nel kernel. Trasmissione interrotta!")
            break
        
        # 3. CREAZIONE E INVIO DEL MESSAGGIO PERIODICO
        try:
            msg = can.Message(
                arbitration_id=TARGET_ID,
                data=[message_counter % 256, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF, 0x00],
                is_extended_id=False
            )
            bus.send(msg)
            print(f"🚀 [Vittima] Messaggio inviato (ID: {hex(TARGET_ID)}). Attesa {TRANSMISSION_PERIOD_SEC}s...")
            message_counter += 1
            time.sleep(TRANSMISSION_PERIOD_SEC) 
        
        except can.CanError as e:
            print(f"⚠️ [Vittima] Errore di trasmissione CAN: {e}. Interruzione.")
            break 
        except OSError as e:
            print(f"❌ [Vittima] Errore di sistema: {e}. Il bus è probabilmente Bus Off.")
            break

    bus.shutdown()
    print("\n🛑 [Vittima] Disconnessa.")

if __name__ == '__main__':
    # Esegui la stessa funzione di utilità nel contesto dello script per la Vittima
    def get_tec_info(interface):
        try:
            command = ['ip', '-details', 'link', 'show', interface]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
            tec_match = re.search(r'tec\s+(\d+)\s+rec\s+(\d+)', output)
            state_match = re.search(r'state\s+(\S+)', output)
            tec_value = int(tec_match.group(1)) if tec_match else -1
            state = state_match.group(1).split('-')[0] if state_match else "UNKNOWN"
            return tec_value, state
        except Exception:
            return -2, "ERROR"
    
    start_victim()
