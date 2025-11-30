#!/usr/bin/env python3
"""
Scenario 1: Bus-off attack su ECU vittima.

- victim_ecu trasmette spesso (es. ogni 5 ms)
- benign_ecu trasmette meno frequentemente
- l'attaccante corrompe SEMPRE i frame della vittima
  -> TEC sale a 256 -> stato BUS_OFF
"""

from can_sim_core import CANNode, CANBus, NodeState


def bus_off_attacker(bus: CANBus, tx_node: CANNode, frame) -> bool:
    """
    Attaccante: se il frame viene dalla vittima, lo rende sempre errato.
    Questo spinge il TEC della vittima verso il BUS_OFF.
    """
    if tx_node.name == "victim_ecu":
        return True   # forziamo errore
    return False      # nessun errore sugli altri


def main():
    # ECU vittima e ECU "benigna"
    victim = CANNode("victim_ecu", base_id=0x200)
    benign = CANNode("benign_ecu", base_id=0x300)

    nodes = [victim, benign]
    bus = CANBus(nodes)

    # periodi di trasmissione (in secondi)
    periods = {
        "victim_ecu": 0.005,   # 5 ms -> molto frequente
        "benign_ecu": 0.050,   # 50 ms
    }

    dt = 0.001  # risoluzione temporale (1 ms)

    print("=== Simulazione BUS-OFF attack ===\n")
    while victim.state != NodeState.BUS_OFF and bus.time < 5.0:
        bus.step(dt, periods, attacker=bus_off_attacker)

    print("\n--- RISULTATO FINALE ---")
    for n in nodes:
        print(f"{n.name:12s}: state={n.state.name:12s} TEC={n.tec} REC={n.rec}")


if __name__ == "__main__":
    main()