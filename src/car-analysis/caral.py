#!/usr/bin/env python
import argparse
import matplotlib.pyplot as plt
import pandas as pd
import re
import seaborn as sns

from caral.core import *
from psutil import net_if_addrs, net_if_stats
from sys import argv


def parse_args():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    # Automotive Ethernet Options
    ae = subparser.add_parser("ae", help="Analyze Automotive Ethernet Protocol")
    ae.add_argument("--iface", help="Specify Ethernet interface for Connection", required=True)
    ae.add_argument("--ip", help="Specify IP to analyze", type=str, required=True)
    ae.add_argument("--protocol", help="Specify connection protocol (Default: UDS)", choices=["tcp", "udp", "uds"], default="uds")

    # CAN Options
    can = subparser.add_parser("can", help="Analyze CAN Protocol")
    can.add_argument("--iface", help="Specify CAN Interface", type=str, required=True)
    can.add_argument("--id", help="Specify CAN ID to analyze", type=str, required=True)
    can.add_argument("--fd", help="Use CAN-FD", action="store_true")

    # FlexRay Options
    fr = subparser.add_parser("fr", help="Analyze FlexRay Protocol")
    fr.add_argument("--channel", help="Specify FlexRay Channel", choices=['A', 'B'], type=str, required=True)

    # LIN Options
    lin = subparser.add_parser("lin", help="Analyze LIN Protocol")
    lin.add_argument("--id", help="Specify LIN ID to analyze")

    parser.add_argument("--device", help="Specify CAN Hardware", choices=["socketcan", "pcan", "etherbadge"], required=True)
    parser.add_argument("--export", help="Export Analysis as CSV", action="store_true")
    parser.add_argument("--plot", help="Plot Graphs", action="store_true")
    parser.add_argument("--verbosity", "-v", help="Control Output verbosity (Default: 1)", choices=['1', '2', '3'], default=1)

    return parser.parse_args()


def plot(evt_df, act_df=None, title_apx=""):
    evt_df = pd.DataFrame(evt_df).groupby(["timestamp"]).count().reset_index()

    # Mock results for testing purposes
    if act_df is not None:
        for i, msg in enumerate(evt_df.msg):
            if i not in act_df:
                evt_df.msg[i] *= 0.8

    evt_df.columns = ["x", "y"]
    reg_order = np.min([20, (len(act_df) * 2 if act_df is not None else 1)])

    print(f"[INFO] Regression Order: {reg_order}")

    # Plot events as bar plot and regression line
    sns.set_style("darkgrid")
    sns.barplot(x=evt_df.x, y=evt_df.y, palette="YlGnBu")
    sns.regplot(x=evt_df.x, y=evt_df.y, order=reg_order, color='r', label="Regression")

    # Plot actions as vertical lines
    if act_df is not None:
        for i, t in enumerate(act_df):
            plt.axvline(t, linestyle='--', color='r', label=f"Action {i+1}")

    # Plot configuration
    plt.legend(loc="lower right")
    plt.ylim(0, np.max(evt_df.y) * 1.1)
    plt.xticks(np.arange(0, np.max(evt_df.x), np.max([1, (len(evt_df.x) // 10)])))
    plt.xlabel("Time (s)")
    plt.ylabel("Message Count")
    plt.title(("Analysis Results " + title_apx))
    plt.show()


def main():
    args = parse_args()
    ifaces = [iface for iface, addr in net_if_addrs().items() if iface in net_if_stats() and getattr(net_if_stats()[iface], "isup")]
    
    if args.plot:
        print(f"[OPTIONS] Plotting enabled: {args.plot}")
    
    if args.verbosity:
        global VERBOSITY
        VERBOSITY = int(args.verbosity)

        print(f"[OPTIONS] Verbosity Level: {VERBOSITY}")

    print(f"[OPTIONS] Hardware: {args.device}")
    print("[INFO] Press 'a' to add Action, 'i' for info, 'q' to stop.")

    inargs = [opt for opt in ["can", "lin", "ae", "fr"] if opt in argv]

    if len(inargs) > 1:
        print(f"[!] More than one Protocol specified ({inargs}). Please choose only one at a time!")
        return

    if "can" in argv:
        global CAN_ID
        CAN_ID = int(args.id, 16)

        if args.iface not in ifaces:
            print(f"[!] Specified interface {args.iface} is not up and running!")
            return

        global CAN_IFACE
        CAN_IFACE = args.iface

        if args.fd:
            global CAN_FD
            CAN_FD = True

        if CAN_ID_MIN <= CAN_ID <= CAN_ID_MAX:
            adf, edf = al_can(CAN_IFACE, CAN_ID)
            adf = adf if len(adf) > 0 else None

            if args.plot:
                plot(evt_df=edf, act_df=adf, title_apx=f"for CAN Traffic (ID: 0x{CAN_ID:03x})")
        else:
            print(f"[!] Invalid CAN ID (must be in range [0x{CAN_ID_MIN:03x}, 0x{CAN_ID_MAX:03x}], is 0x{CAN_ID:03x})")

    if "ae" in argv:
        # Check if input is valid ip address
        if re.match(r'(\b25[0-5]|\b2[0-4][0-9]|\b[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}', args.ip):
            global AE_IP
            AE_IP = args.ip

            if args.iface not in ifaces:
                print(f"[!] Specified interface {args.iface} is not up and running!")
                return

            global AE_IFACE
            AE_IFACE = args.iface

            global AE_PROT
            AE_PROT = args.protocol

            adf, edf = al_ae(AE_IFACE, AE_PROT, AE_IP)
            adf = adf if len(adf) > 0 else None

            if args.plot:
                plot(edf, adf, title_apx=f"for AutoEth Traffic (IP: {AE_IP})")
        else:
            print("[!] Invalid IP Address for Automotive Ethernet")

    if "lin" in argv:
        global LIN_ID
        LIN_ID = int(args.id, 16)

        if LIN_ID_MIN <= LIN_ID <= LIN_ID_MAX:
            adf, edf = al_lin(LIN_ID)
            adf = adf if len(adf) > 0 else None

            if args.plot:
                plot(edf, adf, title_apx=f"for LIN Traffic (ID: {LIN_ID})")

        else:
            print(f"[!] Invalid LIN ID (must be in range [0x{LIN_ID_MIN:02x}, 0x{LIN_ID_MAX:02x}], is 0x{LIN_ID:02x})")

    # TODO: FlexRay
    if "fr" in argv:
        global FR_CHANNEL
        FR_CHANNEL = args.channel

        adf, edf = al_fr(FR_CHANNEL)
        adf = adf if len(adf) > 0 else None

        if args.plot:
            plot(edf, adf, title_apx=f"for FlexRay Traffic (Channel: {FR_CHANNEL})")

    return


if __name__ == "__main__":
    main()
