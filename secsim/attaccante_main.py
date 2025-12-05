# attaccante_main.py
import time
from ecu_base import Role
from att import AttackerECU

def main():
    attacker = AttackerECU(
        victim_id=0x123,
        name="ECU_ATTACKER",
        role=Role.ATTACKER,
        interface="vcan0",
        arbitration_id=0x123,   
        period_sec=0.0,         # non trasmette ciclicamente
    )
    attacker.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        attacker.stop()

if __name__ == "__main__":
    main()