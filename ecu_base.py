# ecu_normale.py
from ecu_base import ECU, Role

def main():
    ecu = ECU(
        name="ECU_NORMAL",
        role=Role.NORMAL,
        interface="vcan0",
        arbitration_id=0x200,
        period_sec=3.0,
    )
    ecu.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ecu.stop()

if __name__ == "__main__":
    main()