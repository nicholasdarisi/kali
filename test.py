"""
Test di comunicazione CAN BUS - Simulazione Bit-Level
Due ECU comunicano tramite Master Controller
"""

import time
from can_master_full import CANMaster, CANSlave


def test_two_ecu_communication():
    """Test: Due ECU che comunicano tranquillamente"""
    
    print("=" * 70)
    print("TEST: COMUNICAZIONE TRA DUE ECU")
    print("=" * 70)
    
    # Crea il master
    master = CANMaster(tick_duration_ms=0.5)
    
    # Crea due ECU normali
    ecu1 = CANSlave(
        name="ECU_1_ENGINE",
        slave_id=1,
        arbitration_id=0x100,
        master=master,
        period_sec=3.0,
        initial_tec=0,
        initial_rec=0
    )
    
    ecu2 = CANSlave(
        name="ECU_2_GEARBOX",
        slave_id=2,
        arbitration_id=0x200,
        master=master,
        period_sec=4.0,
        initial_tec=0,
        initial_rec=0
    )
    
    # Avvia master e slave
    master.start()
    ecu1.start()
    ecu2.start()
    
    try:
        # Lascia comunicare per un po'
        print("\n[TEST] Sistema in esecuzione... (premi Ctrl+C per fermare)")
        print("-" * 70)
        
        for i in range(20):
            time.sleep(1)
            print(f"\n[{i+1}s] Status:")
            print(f"  {ecu1.name}: TEC={ecu1.tec}, REC={ecu1.rec}, state={ecu1.state}")
            print(f"  {ecu2.name}: TEC={ecu2.tec}, REC={ecu2.rec}, state={ecu2.state}")
            print(f"  Master: {master.bus_state.name}")
    
    except KeyboardInterrupt:
        print("\n[TEST] Arresto...")
    
    finally:
        # Arresta tutto
        ecu1.stop()
        ecu2.stop()
        master.stop()
        
        print("\n" + "=" * 70)
        print("RISULTATI FINALI:")
        print("=" * 70)
        print(f"{ecu1.name}:")
        print(f"  TEC={ecu1.tec}, REC={ecu1.rec}")
        print(f"  State={ecu1.state}")
        print(f"  Bit ricevuti: {len(ecu1.received_bits)}")
        
        print(f"\n{ecu2.name}:")
        print(f"  TEC={ecu2.tec}, REC={ecu2.rec}")
        print(f"  State={ecu2.state}")
        print(f"  Bit ricevuti: {len(ecu2.received_bits)}")


def test_multiple_ecu():
    """Test: Tre ECU in comunicazione parallela"""
    
    print("\n" + "=" * 70)
    print("TEST: TRE ECU IN COMUNICAZIONE PARALLELA")
    print("=" * 70)
    
    master = CANMaster(tick_duration_ms=0.5)
    
    ecu1 = CANSlave("ECU_1", 1, 0x100, master, period_sec=2.0)
    ecu2 = CANSlave("ECU_2", 2, 0x200, master, period_sec=2.5)
    ecu3 = CANSlave("ECU_3", 3, 0x300, master, period_sec=3.0)
    
    master.start()
    ecu1.start()
    ecu2.start()
    ecu3.start()
    
    try:
        print("\n[TEST] 3 ECU in comunicazione parallela...")
        for i in range(15):
            time.sleep(1)
            print(f"[{i+1}s] Master: {master.bus_state.name:20s} | "
                  f"ECU1 TX={ecu1.currently_transmitting} | "
                  f"ECU2 TX={ecu2.currently_transmitting} | "
                  f"ECU3 TX={ecu3.currently_transmitting}")
    
    except KeyboardInterrupt:
        pass
    
    finally:
        ecu1.stop()
        ecu2.stop()
        ecu3.stop()
        master.stop()
        
        print("\n" + "=" * 70)
        print("RISULTATI FINALI:")
        print("=" * 70)
        print(f"ECU_1: TEC={ecu1.tec}, REC={ecu1.rec}, Bits RX={len(ecu1.received_bits)}")
        print(f"ECU_2: TEC={ecu2.tec}, REC={ecu2.rec}, Bits RX={len(ecu2.received_bits)}")
        print(f"ECU_3: TEC={ecu3.tec}, REC={ecu3.rec}, Bits RX={len(ecu3.received_bits)}")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("CAN BUS SIMULATOR - TEST SUITE")
    print("#" * 70 + "\n")
    
    # Scegli quale test eseguire
    test_two_ecu_communication()
    # test_multiple_ecu()