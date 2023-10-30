# Car Toolkit

Toolkit providing various tools for automotive penetration testing

## Tools

### CANAttack

```bash
usage: canattack.py [-h] [--interface INTERFACE] [--mitm MITM] [--priorityid PRIORITYID] [--com COM] [--silent] [--compatibility] [--pcan] [--fd] [--baudrate BAUDRATE]

options:
  -h, --help            show this help message and exit
  --interface INTERFACE, -i INTERFACE
                        Specify main CAN interface (vcan0 by default)
  --mitm MITM, -m MITM  Specify Man-In-The-Middle interface (vcan1 by default)
  --priorityid PRIORITYID, -p PRIORITYID
                        Set highest priority id (0x001 by default)
  --com COM, -c COM     Set COM port for serial device (COM9 by default)
  --silent, -s          Suppress superfluous outputs
  --compatibility       Use python-can instead of SocketCAN
  --pcan                Use PCAN USB(-FD) Dongle for Connection
  --fd                  Use for connection to CAN-FD targets
  --baudrate BAUDRATE   Set baudrate of CAN Bus (500 Kbit/s by default)
```

#### Functionality

* Block CAN-BUS (DoS)
* ECU Imitation
* Replay Attack
* MITM Filter Attack
* Read Values via OBD

#### Examples

* `./CANAttack.py -i vcan0 -m vcan1`: default configuration using two virtual CAN interfaces
* `./CANAttack.py -i can0 -m vcan1`: using one physical CAN interface (can0) with vcan1 as MITM bus
* `./CANAttack.py -p 0x001`: Priority ID is 0x001
* `./CANAttack.py -c COM9`: OBDLink SX uses COM-Port 9

### CANReverse

Sanitizes candump .log file and replays it for manual examinations.

```bash
usage: canreverse.py [-h] --file FILE [--sanitize] [--silent] [--interface INTERFACE]

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Specify candump logfile (needs to be sanitized, use --sanitize/-s else)
  --sanitize, -s        Sanitizes file for usage
  --silent              Suppress unnecessary output
  --interface INTERFACE, -i INTERFACE
                        Specify CAN interface (default: vcan0)
```

### CANBrute

Brute Force all possible messages for specific ECU. This is suitbale for lengths up to 4 byte, more will take literally forever. Even though, implemented for up to 8 bytes.

```bash
usage: canbrute.py [-h] --id ID --length LENGTH --interface INTERFACE [--verbose]

options:
  -h, --help            show this help message and exit
  --id ID, -i ID        Arbitration ID to bruteforce
  --length LENGTH, -l LENGTH
                        Message length (1-8 bytes)
  --interface INTERFACE, -I INTERFACE
                        Interface to which message should be send (e.g. can0)
  --verbose, -v         Output current message
```

### Fuzzer Replay

Replays output from caringcaribou uds fuzzer if logging is enabled.

```bash
usage: fuzzer_replay.py [-h] --file FILE --interface INTERFACE

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE
  --interface INTERFACE, -i INTERFACE
```

### Setup Virtual Test Bench

```bash
usage: [sudo] ./setup_vtb.sh [--skip-update] [--random|--icsim]

options:
    -h, --help         show this help message and exit
    --skip-update, -s: Skips environment update before starting the script

    --random, -r:      Generates random can traffic on interface vcan0
    --icsim, -i:       Starts Instrument Cluster Simulation

Note: 
    - either --random or --icsim can be used!
    - sudo can be specified when starting script or will be automatically called while running.
```

#### Examples

* `./setup_vtb.sh --skip-update --random`: skip update and generate random traffic
* `./setup_vtb.sh --icsim`: update and start IC Simulation

## Planned extensions

* XCP integration for ECU recalibration/reprogramming 

## Credits

* PCANBasic: Keneth Wagner ([MacCAN](https://mac-can.github.io/))