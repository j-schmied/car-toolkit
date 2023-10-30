"""
    CANAttack CAN Bus Attack-Software as part of my bachelor's thesis
    "Conception of a prototypical realization of selected attacks on the CAN bus via OBD-II".
    
    Library providing OBDLink-SX support.
    Can be used from within CANAttack or via scapy.

    (c) Jannik Schmied, 2023
"""
import os
import platform
import sys

from .core import is_valid_com_port
from dataclasses import dataclass
from re import match
from time import sleep

import obd

# Show extended error messages
DEBUG: bool = True


@dataclass
class OBDCommands:
    """Implemented OBD Commands for CANAttack"""
    # ELM commands
    ELM_VERSION = obd.commands.ELM_VERSION
    ELM_VOLTAGE = obd.commands.ELM_VOLTAGE

    # ECU commands (Mode 1)
    FUEL = obd.commands.FUEL_STATUS     # 0x03
    RPM = obd.commands.RPM              # 0x0C
    SPEED = obd.commands.SPEED          # 0x0D
    TEMP = obd.commands.COOLANT_TEMP    # 0x05

    # DTC commands (Mode 3, 4, 7)
    CLEAR_DTC = obd.commands.CLEAR_DTC
    CURRENT_DTC = obd.commands.GET_CURRENT_DTC
    GET_DTC = obd.commands.GET_DTC

    # Options
    OPTIONS = [ELM_VERSION, ELM_VOLTAGE, FUEL, RPM, SPEED, TEMP, CLEAR_DTC, CURRENT_DTC, GET_DTC]

    @staticmethod
    def print_options():
        """Print available Commands"""
        print("-" * 56)

        for i, option in enumerate(OBDCommands.OPTIONS):
            print(f"[{i+1}] {option}")

        print("[0] Exit")


class OBDConnection:
    """Object holding connection to OBDLinkSX Adapter"""
    def __init__(self, device: str = "", baud_rate: int = 115200, refresh_rate: int = 1) -> None:
        self.ready = False

        if platform.system() in ["Linux", "Darwin"]:
            self.device = device if os.path.exists(device) else "/dev/tty.usbserial"
        if platform.system() == "Windows":
            self.device = device if is_valid_com_port(device) else "COM9"

        self.baud_rate = baud_rate
        self.refresh_rate = refresh_rate

        try:
            self.connection = obd.OBD(baudrate=self.baud_rate, fast=False)
        except Exception as e:
            print(f"Error: {e}")  # TODO: Add logging logger
            sys.exit(1)

        self.ready = True

    def read(self, cmd) -> None:
        """Using objects connects, execute command"""
        try:
            while True:
                res = self.connection.query(cmd)
                print(f"[*] Response: {cmd!a}: {res}")
                if cmd in [OBDCommands.ELM_VERSION, OBDCommands.ELM_VOLTAGE, OBDCommands.CLEAR_DTC, OBDCommands.CURRENT_DTC, OBDCommands.GET_DTC]:
                    # These commands don't need to be executed multiple times
                    break
                sleep(self.refresh_rate)

        except KeyboardInterrupt:
            print("[!] Stopped. (interrupted by user)")
