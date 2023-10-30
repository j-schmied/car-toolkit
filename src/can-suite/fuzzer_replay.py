#!/usr/bin/env python
"""
    Script to replay fuzzer .log files created by caringcaribou
    (c) Jannik Schmied, 2023
"""
import os
import subprocess
import sys
from argparse import ArgumentParser, Namespace


def parse_args() -> Namespace:
    """Parse command line arguments"""
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--file", "-f", type=str, required=True)
    parser.add_argument("--interface", "-i", type=str, required=True)

    return parser.parse_args()


def main():
    args = parse_args()

    if os.path.exists(args.file):
        with open(args.file, 'r') as messages:
            for msg_data in messages:
                msg = ["cansend", args.interface, msg_data]

                try:
                    proc = subprocess.Popen(msg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"[i] Current: {msg.strip()}", end='\r')
                except KeyboardInterrupt:
                    print("\n[*] Stopped. (Interrupted by user)")
                    exit(0)
                except Exception as e:
                    print("[!] Error:", e)
                finally:
                    proc.terminate()
    else:
        print("[!] Error: file does not exist!")
        sys.exit(1)

    print("\n[+] Finished.\n")
    sys.exit(0)


if __name__ == '__main__':
    main()
