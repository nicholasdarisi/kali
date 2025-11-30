#!/usr/bin/env python3
import can
import time
import argparse

def main():
    parser = argparse.ArgumentParser(description="Normal ECU periodic sender")
    parser.add_argument("--channel", default="vcan0", help="CAN interface (default: vcan0)")
    parser.add_argument("--id", type=lambda x: int(x, 0), default=0x200,
                        help="CAN ID of the ECU (default: 0x200)")
    parser.add_argument("--period", type=float, default=0.05,
                        help="Period between frames in seconds (default: 0.05 = 50ms)")
    args = parser.parse_args()

    bus = can.interface.Bus(channel=args.channel, bustype="socketcan")

    print(f"[+] Normal ECU on {args.channel}, ID=0x{args.id:X}, period={args.period}s")
    print("    Press Ctrl+C to stop")

    try:
        while True:
            msg = can.Message(
                arbitration_id=args.id,
                data=b'\x01\x02\x03\x04\x05\x06\x07\x08',
                is_extended_id=False
            )
            bus.send(msg)
            time.sleep(args.period)
    except KeyboardInterrupt:
        print("\n[+] Stopped normal ECU")

if __name__ == "__main__":
    main()