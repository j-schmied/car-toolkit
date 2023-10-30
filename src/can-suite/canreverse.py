#!/usr/bin/env python3
"""
    CANReverse CAN Bus Reverse-Engineering-Software as part of my bachelors thesis
    "Conception of a prototypical realization of selected attacks on the CAN bus via OBD-II".

    (c) Jannik Schmied, 2023
"""
import sys

from argparse import ArgumentParser, Namespace
from datetime import datetime
from shlex import split
from subprocess import Popen, DEVNULL, PIPE
from time import sleep

from pyfiglet import figlet_format


# Show extended error messages
DEBUG: bool = False

# Constants
VERSION: str = "1.0.0rc1"
FILE: str
SANITIZE: bool = False
SILENT: bool = False
INTERFACE: str = "vcan0"


def parse_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--file", "-f", help="Specify candump logfile (needs to be sanitized, use --sanitize/-s else)", type=str, required=True)
    parser.add_argument("--sanitize", "-s", help="Sanitizes file for usage", action='store_true')
    parser.add_argument("--silent", help="Suppress unnecessary output", action='store_true')
    parser.add_argument("--interface", "-i", help="Specify CAN interface (default: vcan0)", type=str, default="vcan0")

    return parser.parse_args()


def sanitize(file: str) -> str:
    new_file: str = f"candump_logfile_{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}_sanitized.log"
    command: str = f"cat {file}" + " | awk '{print $3}' | sort | uniq" + f" > {new_file}"

    try:
        sanitize_file_process = Popen(split(command), stdout=DEVNULL, stderr=PIPE)
        sanitize_file_process.terminate()
    except Exception as e:
        print("[!] An error occurred:", e)
        sys.exit(1)

    return new_file


def main():
    args = parse_args()

    global FILE
    FILE = args.file

    if args.sanitize:
        global SANITIZE
        SANITIZE = args.sanitize
    if args.silent:
        global SILENT
        SILENT = args.silent
    if args.interface:
        global INTERFACE
        INTERFACE = args.interface

    file: str = FILE

    if not SILENT:
        print("\n", figlet_format("CANREVERSE"))
        print(f"(c) Jannik Schmied, 2022. Version {VERSION}")
        print("-" * 56)

    if SANITIZE:
        print(f"[*] Sanitizing file for further usage...")
        file = sanitize(file)

    try:
        print("[*] Reading file...")
        with open(file, "r") as logfile:
            lines = logfile.readlines()
            packet_counter: int = 0
            for line in lines:
                packet_counter += 1
            send_counter: int = 0

            print("[*] Start reverse engineering process")
            print(f"[i] Total packets: {packet_counter}")
            for line in lines:
                can_message = line
                command = f"cansend {INTERFACE} {can_message}"

                can_message = can_message.replace('\n', '').replace('\r', '')
                print(f"[*] Sending packet {can_message} ({send_counter}/{packet_counter})")
                for counter in range(1):
                    try:
                        send_can_message_process = Popen(split(command), stdout=PIPE, stderr=PIPE)
                        send_counter += 1
                        send_can_message_process.terminate()
                    except Exception as e:
                        print(f"[!] Error: {e}")
                        exit(1)
                sleep(3)
    except FileExistsError:
        print("[!] File not found!")
        sys.exit(1)
    except FileNotFoundError:
        print("[!] File not found!")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[i] Stopped. (Interrupted by user)")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        print(f"[i] Finished! Sent {send_counter} of {packet_counter} packets.")


if __name__ == '__main__':
    main()
