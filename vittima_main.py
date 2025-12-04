# vittima_main.py
import time
from ecu_base import Role
from ecu_base import VictimECU  # se lo metti nello stesso file, basta import

def main():
    victim = VictimECU(
        name="ECU_VICTIM",
        role=Role.VICTIM,
        interface="vcan0",
        arbitration_id=0x123,
        period_sec=2.0,
    )
    victim.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        victim.stop()

if __name__ == "__main__":
    main()