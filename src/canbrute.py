#!/usr/bin/env python3

"""
    Script to Brute Force CAN Messages for a certain Arbitration ID
    (c) Jannik Schmied, 2023
"""
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pyfiglet import figlet_format
from shlex import split


VERBOSE: bool = False


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--id", "-i", help="Arbitration ID to bruteforce", type=str, required=True)
    parser.add_argument("--length", "-l", help="Message length (1-8 bytes)", type=int, required=True)
    parser.add_argument("--interface", "-I", help="Interface to which message should be send (e.g. can0)", type=str, required=True)
    parser.add_argument("--verbose", "-v", help="Output current message", action='store_true')
    return parser.parse_args()


def send_msg(msg):
    try:
        proc = subprocess.Popen(split(msg), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if VERBOSE:
            print(f"[i] Current message: {msg}", end="\r")
    except KeyboardInterrupt:
        print("\n[*] Stopped. (interrupted by user)")
        sys.exit(0)
    except Exception as e:
        print("[!] Error:", e)
    finally:
        proc.terminate()


def b1byte(msg):
    for byte1 in range(0x100):
        tmsg = msg
        tmsg += "{:02x}".format(byte1)
        send_msg(tmsg)


def b2bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            tmsg = msg
            tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2)
            send_msg(tmsg)


def b3bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            for byte3 in range(0x100):
                tmsg = msg
                tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2) + "{:02x}".format(byte3)
                send_msg(tmsg)


def b4bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            for byte3 in range(0x100):
                for byte4 in range(0x100):
                    tmsg = msg
                    tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2) + "{:02x}".format(byte3) + "{:02x}".format(byte4)
                    send_msg(tmsg)


def b5bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            for byte3 in range(0x100):
                for byte4 in range(0x100):
                    for byte5 in range(0x100):
                        tmsg = msg
                        tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2) + "{:02x}".format(byte3) + "{:02x}".format(byte4) + "{:02x}".format(byte5)
                        send_msg(tmsg)


def b6bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            for byte3 in range(0x100):
                for byte4 in range(0x100):
                    for byte5 in range(0x100):
                        for byte6 in range(0x100):
                            tmsg = msg
                            tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2) + "{:02x}".format(byte3) + "{:02x}".format(byte4) + "{:02x}".format(byte5) + "{:02x}".format(byte6)
                            send_msg(tmsg)


def b7bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            for byte3 in range(0x100):
                for byte4 in range(0x100):
                    for byte5 in range(0x100):
                        for byte6 in range(0x100):
                            for byte7 in range(0x100):
                                tmsg = msg
                                tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2) + "{:02x}".format(byte3) + "{:02x}".format(byte4) + "{:02x}".format(byte5) + "{:02x}".format(byte6) + "{:02x}".format(byte7)
                                send_msg(tmsg)


def b8bytes(msg):
    for byte1 in range(0x100):
        for byte2 in range(0x100):
            for byte3 in range(0x100):
                for byte4 in range(0x100):
                    for byte5 in range(0x100):
                        for byte6 in range(0x100):
                            for byte7 in range(0x100):
                                for byte8 in range(0x100):
                                    tmsg = msg
                                    tmsg += "{:02x}".format(byte1) + "{:02x}".format(byte2) + "{:02x}".format(byte3) + "{:02x}".format(byte4) + "{:02x}".format(byte5) + "{:02x}".format(byte6) + "{:02x}".format(byte7) + "{:02x}".format(byte8)
                                    send_msg(tmsg)


def main():
    args = parse_args()

    print(figlet_format("CANBRUTE"))
    print("(c) Jannik Schmied, 2023")
    print("-" * 56)

    if args.length not in list(range(1, 9)):
        print("[!] Invalid length! (must be between 1 and 8)")
        sys.exit(1)

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    print("[*] Running...")

    if not VERBOSE:
        print("[i] Hint: use cansniffer to follow message flow or activate verbose mode (-v).")

    msg = "cansend " + args.interface + " " + args.id + "#"

    match args.length:
        case 1:
            b1byte(msg)
        case 2:
            b2bytes(msg)
        case 3:
            b3bytes(msg)
        case 4:
            b4bytes(msg)
        case 5:
            b5bytes(msg)
        case 6:
            b6bytes(msg)
        case 7:
            b7bytes(msg)
        case 8:
            b8bytes(msg)

    print("\n[+] Finished.\n")
    sys.exit(0)


if __name__ == '__main__':
    main()
