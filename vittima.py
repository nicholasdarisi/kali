import can
import time
import subprocess
import re

# Configurazione
CAN_INTERFACE = 'vcan0'
TARGET_ID = 0x123 # ID del messaggio che l'attaccante prenderà di mira
BUS_OFF_THRESHOLD = 256

def get_tec_from_socketcan(interface):
    """
    Legge il valore di TEC (Transmit Error Counter) dall'interfaccia SocketCAN.
    """
    try:
        command = ['ip', '-details', 'link', 'show', interface]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Cerca la riga che contiene i contatori TEC e REC
        match = re.search(r'tec\s+(\d+)\s+rec\s+(\d+)', result.stdout)
        
        if match:
            return int(match.group(1))
        else:
            return -1 # Valore di errore o non disponibile
            
    except Exception:
        return -2 # Errore di esecuzione

def start_victim():
    """Simula la vittima che trasmette e monitora il suo stato TEC."""
    
    try:
        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')
        print(f"✅ Vittima connessa a {CAN_INTERFACE}. Inizia a trasmettere ID: {hex(TARGET_ID)}")
    except OSError as e:
        print(f"❌ Errore di connessione a {CAN_INTERFACE}: {e}")
        return

    message_counter = 0

    while True:
        tec = get_tec_from_socketcan(CAN_INTERFACE)
        
        if tec >= BUS_OFF_THRESHOLD:
            print(f"\n🚨🚨 [Vittima] BUS OFF RILEVATO! (TEC={tec}). Trasmissione interrotta.")
            break
        elif tec >= 128:
            print(f"🔬 [Vittima] Stato: ERROR PASSIVE (TEC={tec}). Continuo a trasmettere...")
        else:
            print(f"🔬 [Vittima] Stato: ERROR ACTIVE (TEC={tec}). Continuo a trasmettere...")
        
        # Invio del Messaggio Periodico
        try:
            msg = can.Message(
                arbitration_id=TARGET_ID,
                data=[message_counter % 256, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
                is_extended_id=False
            )
            bus.send(msg)
            message_counter += 1
            time.sleep(0.02) # T = 20ms, simile a un ciclo reale
        
        except can.CanError as e:
            print(f"⚠️ [Vittima] Errore di trasmissione CAN: {e}. Probabile Bus Off.")
            break 
        except OSError as e:
            # Cattura errori del sistema operativo (es. "Device not configured")
            print(f"❌ [Vittima] Errore critico di sistema: {e}. Il bus è probabilmente Bus Off.")
            break

    bus.shutdown()
    print("\n🛑 Vittima Disconnessa.")

if __name__ == '__main__':
    start_victim()
