#!/usr/bin/env python3
"""
Core CAN simulator:

- CANNode: controller CAN con TEC, REC, stati (ERROR_ACTIVE, ERROR_PASSIVE, BUS_OFF)
- CANBus: bus con arbitraggio per ID e callback di "attacker"
"""

from enum import Enum, auto


class NodeState(Enum):
    ERROR_ACTIVE = auto()
    ERROR_PASSIVE = auto()
    BUS_OFF = auto()


class CANFrame:
    def __init__(self, arbitration_id: int, dlc: int = 8, data: bytes = b""):
        self.arbitration_id = arbitration_id
        self.dlc = dlc
        self.data = data or bytes([0] * dlc)

    def __repr__(self):
        return f"CANFrame(id=0x{self.arbitration_id:X}, dlc={self.dlc})"


class CANNode:
    """
    Modello logico di un controller CAN:
    - TEC / REC secondo lo standard (semplificato)
    - stati ERROR_ACTIVE / ERROR_PASSIVE / BUS_OFF
    - "period" esterno per decidere quando trasmettere
    """
    def __init__(self, name: str, base_id: int):
        self.name = name
        self.base_id = base_id
        self.tec = 0
        self.rec = 0
        self.state = NodeState.ERROR_ACTIVE
        self.enabled = True  # se BUS_OFF -> False

    # ---------- gestione stati errore ---------- #

    def _update_state(self):
        """Aggiorna lo stato in base a TEC/REC (regole ISO semplificate)."""
        if self.tec >= 256:
            self.state = NodeState.BUS_OFF
            self.enabled = False
        elif self.tec >= 128 or self.rec >= 128:
            self.state = NodeState.ERROR_PASSIVE
        else:
            self.state = NodeState.ERROR_ACTIVE

    def on_tx_success(self):
        # TX corretto: TEC-- (min 0)
        if self.tec > 0:
            self.tec -= 1
        self._update_state()

    def on_rx_success(self):
        # RX corretto: REC-- (min 0)
        if self.rec > 0:
            self.rec -= 1
        self._update_state()

    def on_tx_error(self):
        """
        Errore rilevato dal trasmettitore (bit, ack, form, stuff...).
        Semplificazione:
        - se ERROR_ACTIVE: TEC += 8
        - se ERROR_PASSIVE: TEC += 4
        """
        if self.state == NodeState.ERROR_ACTIVE:
            self.tec += 8
        elif self.state == NodeState.ERROR_PASSIVE:
            self.tec += 4
        self._update_state()

    def on_rx_error(self):
        """
        Errore rilevato da un ricevitore: REC++.
        """
        self.rec += 1
        self._update_state()

    def try_bus_off_recovery(self, idle_steps: int, threshold: int = 128):
        """
        Recupero semplificato dal BUS_OFF:
        dopo un certo numero di slot idle, riduciamo lentamente TEC.
        Quando scende sotto 256, riabilitiamo il nodo (ERROR_PASSIVE).
        """
        if self.state != NodeState.BUS_OFF:
            return

        if idle_steps >= threshold and self.tec > 0:
            self.tec -= 1
            if self.tec < 256:
                self.state = NodeState.ERROR_PASSIVE
                self.enabled = True
        self._update_state()

    # ---------- scheduling trasmissioni ---------- #

    def want_to_transmit(self, t: float, period: float) -> bool:
        """
        Modello periodico: il nodo 'vuole' trasmettere ogni 'period' secondi.
        Implementato come confronto fra slot temporali discreti.
        """
        if not self.enabled:
            return False
        if period <= 0:
            return False
        return int(t / period) != int((t - 1e-9) / period)


class CANBus:
    """
    Bus CAN logico a time-step:
    - decide chi trasmette in ogni slot
    - applica arbitraggio per ID (vince ID più basso)
    - chiama un eventuale 'attacker' per corrompere frame
    """
    def __init__(self, nodes):
        self.nodes = nodes
        self.time = 0.0
        self.idle_steps = 0

    def step(self, dt: float, tx_periods: dict, attacker=None):
        """
        Esegue un time-step di durata dt.

        tx_periods: dict {node.name: period}
        attacker: funzione (bus, tx_node, frame) -> bool (True = errore forzato)
        """
        self.time += dt

        # 1) Nodi che provano a trasmettere in questo slot
        tx_requests = []
        for node in self.nodes:
            period = tx_periods.get(node.name)
            if period is None:
                continue
            if node.want_to_transmit(self.time, period):
                frame = CANFrame(node.base_id)
                tx_requests.append((node, frame))

        if not tx_requests:
            # Bus idle: usato per il recupero dal BUS_OFF
            self.idle_steps += 1
            for n in self.nodes:
                n.try_bus_off_recovery(self.idle_steps)
            return

        self.idle_steps = 0

        # 2) Arbitraggio: vince ID più basso
        tx_requests.sort(key=lambda pair: pair[1].arbitration_id)
        tx_node, frame = tx_requests[0]

        # 3) Attacco: decidiamo se corrompere il frame
        error = False
        if attacker is not None:
            error = attacker(self, tx_node, frame)

        if not error:
            # Trasmissione corretta
            tx_node.on_tx_success()
            for node, _ in tx_requests[1:]:
                # perdenti arbitraggio -> niente errore
                pass
            for node in self.nodes:
                if node is not tx_node:
                    node.on_rx_success()
            print(f"[{self.time:8.4f}s] TX OK    from {tx_node.name:12s} "
                  f"ID=0x{frame.arbitration_id:X}")
        else:
            # Frame corrotto: errore TX + RX
            tx_node.on_tx_error()
            for node in self.nodes:
                if node is not tx_node:
                    node.on_rx_error()
            print(f"[{self.time:8.4f}s] TX ERROR from {tx_node.name:12s} "
                  f"ID=0x{frame.arbitration_id:X}")

        # 4) Stampa stato sintetico
        for n in self.nodes:
            print(f"   {n.name:12s}: state={n.state.name:12s} "
                  f"TEC={n.tec:3d}  REC={n.rec:3d}")
        print()