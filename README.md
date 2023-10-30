# Car Toolkit

Toolkit providing various tools for automotive penetration testing

## Tools

- CAN Suite (CANAttack, CANReverse, CANBrute)
- CARAL

## Scripts

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

- `./setup_vtb.sh --skip-update --random`: skip update and generate random traffic
- `./setup_vtb.sh --icsim`: update and start IC Simulation

### Setup CAN Interface

```bash
usage: ./setup_can.sh <interface> <bitrate>

options:
  --fd:             Enables CAN-FD mode

Valid interfaces: [v|sl]can[0-9]
Valid bitrates: 10, 20, 50, 125, 250, 500, 800, 1000, 2000*, 5000*, 8000* (kbit/s)

* CAN-FD only
```

#### Examples

- `./setup_can.sh can0 1000`
- `./setup_can.sh can0 8000 --fd`
