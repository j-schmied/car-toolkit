# Car Toolkit

Toolkit providing various tools for automotive penetration testing

## Tools

### CANAttack

**Command Line Arguments**

* -i: Hauptinterface festlegen (Standardmäßig vcan0)
* -m: MITM-Interface festlegen (Standardmäßig vcan1)
* -p: Priority ID festlegen (Standardmäßig 0x000)
* -c: COM Port für OBDLink SX festlegen
* -s: Silent Mode (less output)
* --compatibility: Use python-can anstatt socketcan
* --pcan: Use PEAK PCAN USB (FD) für CAN Connnection
* --fd: Enable CAN FD compatiblity
* --baudrate: Specify baudrate for CAN Bus

**Angriffe**

* Block CAN-BUS (DoS)
* ECU Imitation
* Replay Attack
* MITM Filter Attack
* Read Values via OBD

**Beispiele**

* `./CANAttack.py -i vcan0 -m vcan1`: Standardkonfiguration mit virtuellen Bussen
* `./CANAttack.py -i can0 -m vcan1`: Benutzung eines physischen CAN-Interface mit vcan1 als MITM Bus
* `./CANAttack.py -p 0x001`: Priority ID ist 0x001
* `./CANAttack.py -c COM9`: OBDLink SX benutzt COM-Port 9

### CANReverse

Sanitizes candump .log file and replays it for manual examinations.

**Command Line Arguments**

* -f: Specify candump file path
* -s: Sanitize file
* -s: Less output
* -i: Specify CAN interface

### CANBrute

Brute Force all possible messages for specific ECU. This is suitbale for lengths up to 4 byte, more will take literally forever. Even though, implemented for up to 8 bytes.

**Command Line Arguments**

* -i: Arbitration ID
* -l: Length of CAN Frame Data
* -I: Specify CAN interface
* -v: Print current message to stdout (instead, use cansniffer, ~5% faster)

### Fuzzer Replay

Replays output from caringcaribou uds fuzzer if logging is enabled.

**Command Line Arguments**

* -f: Specify log file path
* -i: Specify CAN interface

### Setup Virtual Test Bench

**Command Line Arguments**

* --help|-h:     Hilfe anzeigen
* --random:      zufälligen Traffic auf CAN-Interface vcan0 erzeugen
* --icsim:       Insturment Cluster Simulation starten
* --skip-update: Systemupdate überspringen

**Beispiele**

* `./setup_vtb.sh --help`: Hilfe
* `./setup_vtb.sh --skip-update --random`: Update überspringen und zufälligen Traffic
* `./setup_vtb.sh --icsim`: Update und IC Simulation

## Planned extensions

* XCP integration for ECU recalibration/reprogramming 

## Credits

* PCANBasic: Keneth Wagner ([MacCAN](https://mac-can.github.io/))