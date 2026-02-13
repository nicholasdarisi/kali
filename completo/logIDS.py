====================================================================================================
CAN BUS SIMULATOR - DYNAMIC ARBITRATION TEST
====================================================================================================

Configurazione:
  - ECU con ID MINORE (priorita ALTA) -> periodo MAGGIORE (trasmette MENO spesso)
  - ECU con ID MAGGIORE (priorita BASSA) -> periodo MINORE (trasmette PIU spesso)
  - 2 ECU con STESSO ID -> generano COLLISION e incrementano TEC


Scenari testati:
  1. ECU singola che trasmette da sola
  2. Arbitraggio tra ECU con ID diversi
  3. Collision tra ECU con stesso ID
  4. ECU che vuole trasmettere mentre un'altra sta trasmettendo


CORREZIONI IMPLEMENTATE:
  - START_SLOT eliminato: tutte le ECU PENDING partecipano SUBITO all'arbitraggio
  - Collision: ENTRAMBE le ECU incrementano TEC di +8
  - ERROR FLAG ACTIVE: 6 bit DOMINANT (TEC < 128)
  - ERROR FLAG PASSIVE: 8 bit RECESSIVE (TEC >= 128)
  - TEC -= 1 dopo trasmissione con successo
  - ERROR FLAG PASSIVE: +8 errore, -1 successo = +7 netto

[MASTER] SocketCAN OK su vcan0
[MASTER] START
ECU configurate:
  - ECU_A: ID=0x050 (priorita ALTA)        -> TX ogni 6.0s  (start: 0.1s)
  - ECU_B: ID=0x100 (priorita MEDIA-ALTA)  -> TX ogni 8.0s  (start: 2.0s)
  - ECU_C: ID=0x200 (priorita MEDIA-BASSA) -> TX ogni 10.0s (start: 2.0s)
  - ECU_D: ID=0x300 (priorita BASSA)       -> TX ogni 12.0s (start: 4.0s)
  - ECU_E: ID=0x300 (COLLISION con D!)     -> TX ogni 14.0s (start: 4.0s)

====================================================================================================
[ECU_A] START slave_id=1 ID=0x050 period=6.00s
[ECU_B] START slave_id=2 ID=0x100 period=8.00s
[ECU_C] START slave_id=3 ID=0x200 period=10.00s
[ECU_D] START slave_id=4 ID=0x300 period=14.00s
[ECU_E] START slave_id=5 ID=0x300 period=14.00s

Simulazione avviata! (Ctrl+C per fermare)

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B, ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B, ECU_C
  [ARB] SOF          | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_C=1 -> BUS=0
  [ARB] ECU_C perde arbitraggio
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.10s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.01s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.01s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.00s
  [ECU_E ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.00s
====================================================================================================

[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=8 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.10s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.01s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.01s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 12.02s
  [ECU_E ] ID=0x300 | TEC=  8 REC=  0 | ERROR_ACTIVE  | Attende 12.02s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.13s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.01s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.01s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.02s
  [ECU_E ] ID=0x300 | TEC=  8 REC=  0 | ERROR_ACTIVE  | Attende 9.02s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.13s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.05s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.01s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.02s
  [ECU_E ] ID=0x300 | TEC=  8 REC=  0 | ERROR_ACTIVE  | Attende 6.02s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_C
  [ARB] SOF          | ECU_A=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_C=1 -> BUS=0
  [ARB] ECU_C perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.16s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.05s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.06s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.02s
  [ECU_E ] ID=0x300 | TEC=  8 REC=  0 | ERROR_ACTIVE  | Attende 3.02s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.16s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.04s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.05s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.02s
  [ECU_E ] ID=0x300 | TEC=  8 REC=  0 | ERROR_ACTIVE  | Attende 0.02s
====================================================================================================

[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=8 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_B, ECU_D, ECU_E
  [ARB] SOF          | ECU_A=0 | ECU_B=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 | ECU_D=1 | ECU_E=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
  [ARB] ECU_E perde arbitraggio
  [ARB] ID           | ECU_A=0 | ECU_B=1 -> BUS=0
  [ARB] ECU_B perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B, ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B, ECU_D, ECU_E
  [ARB] SOF          | ECU_B=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_D=1 | ECU_E=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
  [ARB] ECU_E perde arbitraggio
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=16 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.19s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.08s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.05s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 11.03s
  [ECU_E ] ID=0x300 | TEC= 16 REC=  0 | ERROR_ACTIVE  | Attende 11.03s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.18s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.08s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.06s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.03s
  [ECU_E ] ID=0x300 | TEC= 16 REC=  0 | ERROR_ACTIVE  | Attende 8.03s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.22s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.12s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.05s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.03s
  [ECU_E ] ID=0x300 | TEC= 16 REC=  0 | ERROR_ACTIVE  | Attende 5.03s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.22s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.12s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.05s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.03s
  [ECU_E ] ID=0x300 | TEC= 16 REC=  0 | ERROR_ACTIVE  | Attende 2.03s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=16 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_E
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C, ECU_D, ECU_E
  [ARB] SOF          | ECU_C=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_C=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_C=1 | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_C=0 | ECU_D=1 | ECU_E=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
  [ARB] ECU_E perde arbitraggio
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=24 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  1 | ERROR_ACTIVE  | Attende 3.25s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  1 | ERROR_ACTIVE  | Attende 1.12s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  1 | ERROR_ACTIVE  | Attende 9.06s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | PENDING
  [ECU_E ] ID=0x300 | TEC= 24 REC=  0 | ERROR_ACTIVE  | Attende 13.05s
====================================================================================================


[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.25s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.16s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.06s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 10.05s
  [ECU_E ] ID=0x300 | TEC= 24 REC=  0 | ERROR_ACTIVE  | Attende 10.05s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.28s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.16s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.05s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.05s
  [ECU_E ] ID=0x300 | TEC= 24 REC=  0 | ERROR_ACTIVE  | Attende 7.05s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.28s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.16s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.05s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.05s
  [ECU_E ] ID=0x300 | TEC= 24 REC=  0 | ERROR_ACTIVE  | Attende 4.05s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_B, ECU_C
  [ARB] SOF          | ECU_A=0 | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 | ECU_C=1 -> BUS=0
  [ARB] ECU_C perde arbitraggio
  [ARB] ID           | ECU_A=0 | ECU_B=1 -> BUS=0
  [ARB] ECU_B perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B, ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B, ECU_C
  [ARB] SOF          | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_C=1 -> BUS=0
  [ARB] ECU_C perde arbitraggio
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.32s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.20s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.10s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.05s
  [ECU_E ] ID=0x300 | TEC= 24 REC=  0 | ERROR_ACTIVE  | Attende 1.05s
====================================================================================================

[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=24 REC=0 State=ERROR_ACTIVE
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=32 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.32s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.20s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.10s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 12.07s
  [ECU_E ] ID=0x300 | TEC= 32 REC=  0 | ERROR_ACTIVE  | Attende 12.07s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.37s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.25s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.10s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.07s
  [ECU_E ] ID=0x300 | TEC= 32 REC=  0 | ERROR_ACTIVE  | Attende 9.07s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.37s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.25s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.11s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.07s
  [ECU_E ] ID=0x300 | TEC= 32 REC=  0 | ERROR_ACTIVE  | Attende 6.07s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.41s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.25s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.11s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.07s
  [ECU_E ] ID=0x300 | TEC= 32 REC=  0 | ERROR_ACTIVE  | Attende 3.07s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.41s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.29s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.11s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.07s
  [ECU_E ] ID=0x300 | TEC= 32 REC=  0 | ERROR_ACTIVE  | Attende 0.07s
====================================================================================================

[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D
[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=32 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=40 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=1 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_D
  [ARB] SOF          | ECU_A=0 | ECU_D=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_D=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_D=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.45s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.29s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.15s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 11.09s
  [ECU_E ] ID=0x300 | TEC= 40 REC=  0 | ERROR_ACTIVE  | Attende 11.09s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.45s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.29s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.15s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.09s
  [ECU_E ] ID=0x300 | TEC= 40 REC=  0 | ERROR_ACTIVE  | Attende 8.09s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_B
  [ARB] SOF          | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=1 -> BUS=0
  [ARB] ECU_B perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.47s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.32s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.15s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.09s
  [ECU_E ] ID=0x300 | TEC= 40 REC=  0 | ERROR_ACTIVE  | Attende 5.09s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.47s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.32s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.15s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.09s
  [ECU_E ] ID=0x300 | TEC= 40 REC=  0 | ERROR_ACTIVE  | Attende 2.09s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=40 REC=0 State=ERROR_ACTIVE
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B, ECU_D, ECU_E
  [ARB] SOF          | ECU_B=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_D=1 | ECU_E=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
  [ARB] ECU_E perde arbitraggio
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=48 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  1 | ERROR_ACTIVE  | Attende 3.50s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  1 | ERROR_ACTIVE  | Attende 7.36s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  1 | ERROR_ACTIVE  | Attende 7.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | PENDING
  [ECU_E ] ID=0x300 | TEC= 48 REC=  0 | ERROR_ACTIVE  | Attende 13.11s
====================================================================================================


[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.50s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.36s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 10.11s
  [ECU_E ] ID=0x300 | TEC= 48 REC=  0 | ERROR_ACTIVE  | Attende 10.11s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.53s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.36s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.11s
  [ECU_E ] ID=0x300 | TEC= 48 REC=  0 | ERROR_ACTIVE  | Attende 7.11s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B, ECU_C
  [ARB] SOF          | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_C=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_C=1 -> BUS=0
  [ARB] ECU_C perde arbitraggio
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.53s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.40s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.11s
  [ECU_E ] ID=0x300 | TEC= 48 REC=  0 | ERROR_ACTIVE  | Attende 4.11s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.57s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.40s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.11s
  [ECU_E ] ID=0x300 | TEC= 48 REC=  0 | ERROR_ACTIVE  | Attende 1.11s
====================================================================================================

[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=48 REC=0 State=ERROR_ACTIVE
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=56 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.56s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.40s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 12.13s
  [ECU_E ] ID=0x300 | TEC= 56 REC=  0 | ERROR_ACTIVE  | Attende 12.13s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_B
  [ARB] SOF          | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=1 -> BUS=0
  [ARB] ECU_B perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.59s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.44s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.13s
  [ECU_E ] ID=0x300 | TEC= 56 REC=  0 | ERROR_ACTIVE  | Attende 9.13s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.59s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.44s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.13s
  [ECU_E ] ID=0x300 | TEC= 56 REC=  0 | ERROR_ACTIVE  | Attende 6.13s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.62s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.48s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.13s
  [ECU_E ] ID=0x300 | TEC= 56 REC=  0 | ERROR_ACTIVE  | Attende 3.13s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.62s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.48s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.20s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.13s
  [ECU_E ] ID=0x300 | TEC= 56 REC=  0 | ERROR_ACTIVE  | Attende 0.13s
====================================================================================================

[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=56 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_E
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C, ECU_D, ECU_E
  [ARB] SOF          | ECU_C=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_C=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_C=1 | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_C=0 | ECU_D=1 | ECU_E=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
  [ARB] ECU_E perde arbitraggio
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_D, ECU_E
  [ARB] SOF          | ECU_A=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_D=1 | ECU_E=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
  [ARB] ECU_E perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=64 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.65s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.48s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.25s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 11.15s
  [ECU_E ] ID=0x300 | TEC= 64 REC=  0 | ERROR_ACTIVE  | Attende 11.15s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.65s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.52s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.25s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.15s
  [ECU_E ] ID=0x300 | TEC= 64 REC=  0 | ERROR_ACTIVE  | Attende 8.15s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.68s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.52s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.25s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.15s
  [ECU_E ] ID=0x300 | TEC= 64 REC=  0 | ERROR_ACTIVE  | Attende 5.15s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.68s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.52s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 8.30s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.15s
  [ECU_E ] ID=0x300 | TEC= 64 REC=  0 | ERROR_ACTIVE  | Attende 2.15s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_B
  [ARB] SOF          | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=1 -> BUS=0
  [ARB] ECU_B perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D
[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=64 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=72 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.71s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.56s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 5.30s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 13.17s
  [ECU_E ] ID=0x300 | TEC= 72 REC=  0 | ERROR_ACTIVE  | Attende 13.17s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.71s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.56s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 2.30s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 10.17s
  [ECU_E ] ID=0x300 | TEC= 72 REC=  0 | ERROR_ACTIVE  | Attende 10.17s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.74s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.60s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.30s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.17s
  [ECU_E ] ID=0x300 | TEC= 72 REC=  0 | ERROR_ACTIVE  | Attende 4.17s
====================================================================================================

[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.77s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.60s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.30s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 1.17s
  [ECU_E ] ID=0x300 | TEC= 72 REC=  0 | ERROR_ACTIVE  | Attende 1.17s
====================================================================================================

[ECU_E] VUOLE TRASMETTERE (ID=0x300) TEC=72 REC=0 State=ERROR_ACTIVE
[ECU_D] VUOLE TRASMETTERE (ID=0x300) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D, ECU_E

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D, ECU_E
  [ARB] SOF          | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] ID           | ECU_D=0 | ECU_E=0 -> BUS=0
  [ARB] RTR          | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] COLLISION! Stesso ID/RTR: ECU_D,ECU_E -> TRANSMIT (errore imminente)
  [TX]  IDE          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  R0           | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DLC          | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=1 | ECU_E=1 -> BUS=1
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=1 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_E (offender=bit_monitoring) -> error flag dominante, frame abortito
[MASTER] ECU_E: TEC=80 (+8 per errore ACTIVE) State=ERROR_ACTIVE
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
  [TX]  STUFF        | ECU_D=1 | ECU_E=0 -> BUS=0

[MASTER] BIT ERROR (ACTIVE) rilevato da ECU_D (offender=bit_monitoring) -> error flag dominante, frame abortito
  [TX]  DATA         | ECU_D=0 | ECU_E=0 -> BUS=0
[MASTER] Frame ERROR -> Retransmission
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D
[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=1 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B, ECU_D
  [ARB] SOF          | ECU_B=0 | ECU_D=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_D=0 -> BUS=0
  [ARB] ID           | ECU_B=0 | ECU_D=1 -> BUS=0
  [ARB] ECU_D perde arbitraggio
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_A: REC=0 (-1 per frame OK ricevuto)
[MASTER] ECU_C: REC=0 (-1 per frame OK ricevuto)
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_D

[MASTER] IDLE->ARBITRATION | Contenders: ECU_D
  [ARB] SOF          | ECU_D=0 -> BUS=0
[MASTER] WINNER: ECU_D (ID=0x300) -> TRANSMIT
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  ID           | ECU_D=0
  [TX]  RTR          | ECU_D=0
  [TX]  IDE          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  R0           | ECU_D=1
  [TX]  DLC          | ECU_D=1
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DLC          | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=1
  [TX]  DATA         | ECU_D=0
  [TX]  DATA         | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  STUFF        | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=0
  [TX]  CRC          | ECU_D=1
  [TX]  CRC          | ECU_D=0
  [TX]  CRC_DELIM    | ECU_D=1
  [TX]  ACK_SLOT     | ECU_D=1
  [TX]  ACK_DELIM    | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  EOF          | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
  [TX]  INTERMISSION | ECU_D=1
[MASTER] Frame OK: ID=0x300 data=0404040404040404
[MASTER] ECU_D: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] ECU_B: REC=0 (-1 per frame OK ricevuto)

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.77s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.64s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.30s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 12.19s
  [ECU_E ] ID=0x300 | TEC= 80 REC=  0 | ERROR_ACTIVE  | Attende 12.19s
====================================================================================================

[ECU_C] VUOLE TRASMETTERE (ID=0x200) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_C

[MASTER] IDLE->ARBITRATION | Contenders: ECU_C
  [ARB] SOF          | ECU_C=0 -> BUS=0
[MASTER] WINNER: ECU_C (ID=0x200) -> TRANSMIT
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  ID           | ECU_C=0
  [TX]  RTR          | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  IDE          | ECU_C=0
  [TX]  R0           | ECU_C=1
  [TX]  DLC          | ECU_C=1
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DLC          | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=0
  [TX]  STUFF        | ECU_C=1
  [TX]  DATA         | ECU_C=0
  [TX]  DATA         | ECU_C=1
  [TX]  DATA         | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=1
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC          | ECU_C=0
  [TX]  CRC_DELIM    | ECU_C=1
  [TX]  ACK_SLOT     | ECU_C=1
  [TX]  ACK_DELIM    | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  EOF          | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
  [TX]  INTERMISSION | ECU_C=1
[MASTER] Frame OK: ID=0x200 data=0303030303030303
[MASTER] ECU_C: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_A

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A
  [ARB] SOF          | ECU_A=0 -> BUS=0
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE

====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.80s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 3.64s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 7.35s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 9.19s
  [ECU_E ] ID=0x300 | TEC= 80 REC=  0 | ERROR_ACTIVE  | Attende 9.19s
====================================================================================================


====================================================================================================
STATUS BUS (IDLE)
====================================================================================================
  [ECU_A ] ID=0x050 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.80s
  [ECU_B ] ID=0x100 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 0.64s
  [ECU_C ] ID=0x200 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 4.35s
  [ECU_D ] ID=0x300 | TEC=  0 REC=  0 | ERROR_ACTIVE  | Attende 6.19s
  [ECU_E ] ID=0x300 | TEC= 80 REC=  0 | ERROR_ACTIVE  | Attende 6.19s
====================================================================================================

[ECU_B] VUOLE TRASMETTERE (ID=0x100) TEC=0 REC=0 State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B
[ECU_A] VUOLE TRASMETTERE (ID=0x050) TEC=0 REC=0 State=ERROR_ACTIVE

[MASTER] IDLE->ARBITRATION | Contenders: ECU_A, ECU_B
  [ARB] SOF          | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=0 -> BUS=0
  [ARB] ID           | ECU_A=0 | ECU_B=1 -> BUS=0
  [ARB] ECU_B perde arbitraggio
[MASTER] WINNER: ECU_A (ID=0x050) -> TRANSMIT
  [TX]  ID           | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=1
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  ID           | ECU_A=0
  [TX]  RTR          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  IDE          | ECU_A=0
  [TX]  R0           | ECU_A=1
  [TX]  DLC          | ECU_A=1
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DLC          | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=0
  [TX]  DATA         | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=0
  [TX]  STUFF        | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=1
  [TX]  CRC          | ECU_A=0
  [TX]  CRC          | ECU_A=1
  [TX]  CRC_DELIM    | ECU_A=1
  [TX]  ACK_SLOT     | ECU_A=1
  [TX]  ACK_DELIM    | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  EOF          | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
  [TX]  INTERMISSION | ECU_A=1
[MASTER] Frame OK: ID=0x050 data=0101010101010101
[MASTER] ECU_A: TEC=0 (-1 per successo) State=ERROR_ACTIVE
[MASTER] IDLE: gather window (0.30s) | Pending now: ECU_B

[MASTER] IDLE->ARBITRATION | Contenders: ECU_B
  [ARB] SOF          | ECU_B=0 -> BUS=0
[MASTER] WINNER: ECU_B (ID=0x100) -> TRANSMIT
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  ID           | ECU_B=0
  [TX]  RTR          | ECU_B=0
  [TX]  IDE          | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  R0           | ECU_B=1
  [TX]  DLC          | ECU_B=1
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DLC          | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  STUFF        | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=0
  [TX]  DATA         | ECU_B=1
  [TX]  DATA         | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=1
  [TX]  STUFF        | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC          | ECU_B=0
  [TX]  CRC          | ECU_B=1
  [TX]  CRC_DELIM    | ECU_B=1
  [TX]  ACK_SLOT     | ECU_B=1
  [TX]  ACK_DELIM    | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  EOF          | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
  [TX]  INTERMISSION | ECU_B=1
[MASTER] Frame OK: ID=0x100 data=0202020202020202
[MASTER] ECU_B: TEC=0 (-1 per successo) State=ERROR_ACTIVE


Simulazione interrotta manualmente

====================================================================================================
[FINAL STATUS]
====================================================================================================
  ECU_A: TEC=  0 REC=  0 State=ERROR_ACTIVE
  ECU_B: TEC=  0 REC=  0 State=ERROR_ACTIVE
  ECU_C: TEC=  0 REC=  0 State=ERROR_ACTIVE
  ECU_D: TEC=  0 REC=  0 State=ERROR_ACTIVE
  ECU_E: TEC= 80 REC=  0 State=ERROR_ACTIVE
====================================================================================================

[MASTER] STOP
