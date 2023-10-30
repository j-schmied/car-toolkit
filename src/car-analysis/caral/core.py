import ics as icsneo
import keyboard as kb
import numpy as np

from caral.config import *
from caral.libs.PCANBasic import *
from caral.libs.PLinApi import *
from datetime import datetime
from scapy.contrib.cansocket_python_can import CANSocket


def get_timestamp(t0) -> int:
    return (datetime.now() - t0).seconds


def gethms(t):
    h = t // 3600
    m = t // 60 - h * 60
    s = t - h * 3600 - m * 60
    return f"{h} h {m} min {s} s"


def al_can(interface, can_id) -> tuple:
    print("[CAN] Starting Analysis")
    print(f"[CAN] ID: 0x{can_id:03x}")
    print(f"[CAN] Interface: {interface}")
    print(f"[CAN] FD Mode: {CAN_FD}")

    match interface:
        case "socketcan":
            # Setup CAN Socket
            try:
                socket = CANSocket(channel=interface)
            except Exception as e:
                print(f"[!] Error initializing CAN Socket: {e}")
                exit()

        case "pcan":
            pcan = PCANBasic()
            channel = PCAN_USBBUS1

            # Initialize PCAN Adapter
            if CAN_FD:
                result = pcan.InitializeFD(channel, PCAN_BAUD_500K)
            else:
                result = pcan.Initialize(channel, PCAN_BAUD_1M)

            # Check if init was successful
            if result[0] != PCAN_ERROR_OK:
                print(f"[!] Error: {pcan.GetErrorText(result)}")
                exit()

        case "etherbadge":
            devices = icsneo.find_devices()
            if len(devices) > 0:
                for device in devices:
                    print(f"[+] Device found: {device.Name} ({device.SerialNumber})")
            else:
                print("[-] No devices found")

    action_list = list()
    event_list = list()
    info_list = list()
    msg_count = 0
    others_count = 0
    t0 = datetime.now()

    # Analysis Loop
    while True:
        try:
            t = get_timestamp(t0)

            if kb.is_pressed('a'):
                if t not in action_list and (t-1) not in action_list:
                    action_list.append(t)
                    print(f"[+] Added action at t = {t}")

            if kb.is_pressed('q'):
                tend = get_timestamp(t0)
                print(f"[!] Stopped at t = {tend} ({gethms(tend)})")
                break

            if kb.is_pressed('i'):
                if t not in info_list and (t-1) not in info_list:
                    info_list.append(t)
                    print(f"[INFO] t = {get_timestamp(t0)}, {msg_count} messages with CAN ID 0x{can_id:03x}, {len(action_list)} actions happend")

            if kb.is_pressed('v'):
                global VERBOSITY
                VERBOSITY = np.min([3, (VERBOSITY + 1)])
                print(f"[INFO] Verbosity Level: {VERBOSITY}")

            match interface:
                case "socketcan":
                    msg = socket.recv()
                case "pcan":
                    result = msg = pcan.Read(channel)
                    if result[0] != PCAN_ERROR_OK:
                        print(f"[!] Error: {pcan.GetErrorText(result)}")
                        continue
                case "etherbadge":
                    pass

            if msg.identifier != can_id:
                others_count += 1
                continue

            if VERBOSITY == 3:
                print(f"[INFO] {msg.data}")

            evt = dict()
            evt["msg"] = msg.data
            evt["timestamp"] = get_timestamp(t0)
            event_list.append(evt)
            msg_count += 1

        except KeyboardInterrupt:
            print(f"[!] Stopped on SIGINT ({get_timestamp(t0)})")
            break

        except Exception as e:
            print(f"[!] Error: {e}")
            exit()

    if VERBOSITY >= 2:
        print(f"[INFO] Messages received with ID {can_id}: {msg_count}")
        print(f"[INFO] Other messages received: {others_count}")

    match interface:
        case "socketcan":
            socket.close()
        case "pcan":
            pcan.Uninitialize(channel)
        case "etherbadge":
            pass

    return action_list, event_list


def al_ae(interface, prot, ip) -> tuple:
    print("[AE] Starting Analysis")
    print(f"[AE] IP: {ip}")
    print(f"[AE] Interface: {interface}")
    print(f"[AE] Protocol: {prot}")

    # TODO: Setup Ethernet Socket based on protocol
    try:
        match prot:
            case "udp":
                # socket = L3RawSocket(iface=interface)
                pass
            case "uds":
                # socket = UDS_DoIPSocket(ip)
                pass
            case "tcp":
                # socket = DoIPSocket(ip)
                pass
    except Exception as e:
        print(f"[!] Error initializing Ethernet Socket: {e}")
        exit()

    action_list = list()
    event_list = list()
    info_list = list()
    msg_count = 0
    others_count = 0
    t0 = datetime.now()

    # Analysis Loop
    while True:
        try:
            t = get_timestamp(t0)

            if kb.is_pressed('a'):
                if t not in action_list and (t - 1) not in action_list:
                    action_list.append(t)
                    print(f"[+] Added action at t = {t}")

            if kb.is_pressed('q'):
                tend = get_timestamp(t0)
                print(f"[!] Stopped at t = {tend} ({gethms(tend)})")
                break

            if kb.is_pressed('i'):
                if t not in info_list and (t - 1) not in info_list:
                    info_list.append(t)
                    print(f"[INFO] t = {get_timestamp(t0)}, {msg_count} messages with IP {ip}, {len(action_list)} actions happend")

            if kb.is_pressed('v'):
                global VERBOSITY
                VERBOSITY = np.min([3, (VERBOSITY + 1)])

            # TODO: Remove mocking
            if np.random.uniform(0, 1) > 0.5:
                msg = {"ip": "192.168.1.4", "data": "Test"}
            else:
                continue

            # TODO: msg = socket.recv()

            if msg["ip"] != ip:
                others_count += 1
                continue

            if VERBOSITY == 3:
                print(f"[INFO] {msg['data']}")

            evt = dict()
            evt["msg"] = msg["data"]
            evt["timestamp"] = get_timestamp(t0)
            event_list.append(evt)
            msg_count += 1

        except KeyboardInterrupt:
            print(f"[!] Stopped on SIGINT (t = {get_timestamp(t0)})")
            break

        except Exception as e:
            print(f"[!] Error: {e}")
            exit()

    if VERBOSITY >= 2:
        print(f"[INFO] Messages received with IP {ip}: {msg_count}")
        print(f"[INFO] Other messages received: {others_count}")

    # TODO: socket.close()

    return action_list, event_list


def al_lin(lin_id):
    print("[LIN] Starting Analysis")
    print(f"[LIN] ID: 0x{lin_id:02x}")

    action_list = list()
    event_list = list()
    info_list = list()
    msg_count = 0
    others_count = 0
    t0 = datetime.now()

    # TODO: Read API and adapt
    plin = PLinApi.InitializeHardware()

    # while True:
    msg = PLinApi.Read()

    return action_list, event_list


def al_fr(ch):
    print("[FR] Starting Analysis")
    print(f"[FR] Channel {ch}")

    action_list = list()
    event_list = list()
    info_list = list()
    msg_count = 0
    others_count = 0
    t0 = datetime.now()

    # TODO: Message Handling

    return action_list, event_list
