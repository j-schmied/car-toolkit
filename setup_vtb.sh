#!/usr/bin/env bash

#######################################
# Setup script for virtual test bench #
#######################################

# Catch command line arguments
BASE_PATH=$(pwd) # path where ICSim folder is located
PKG_MANAGER=apt-get
CLI_ARGUMENTS=$*
# VALID_ARGUMENTS="--help -h --skip-update -s --random -r --icsim -i"

stty -echoctl # hide ^C

print_help() {
  echo "usage: [sudo] ./setup_vtb [--help][--skip-update] [--random|--icsim]"
  echo
  echo -e "options:"
  echo -e "  --help, -h:        show this help message and exit"
  echo -e "  --skip-update, -s: Skips environment update before starting the script"
  echo
  echo -e "  --random, -r:      Generates random can traffic on interface vcan0"
  echo -e "  --icsim, -i:       Starts Instrument Cluster Simulation"
  echo
  echo -e "Note:" 
  echo -e "  - either --random or --icsim can be used!"
  echo -e "  - sudo can be specified when starting script or will be automatically called while running."
}

# Display help and exit (you better not proceed before getting help)
if [[ "$CLI_ARGUMENTS" == *"--help"* || "$CLI_ARGUMENTS" == *"-h"* ]]; then
  print_help
  exit
fi

# Check command line arguments validity
# Either --random or --icsim must be chosen
if [[ ("$CLI_ARGUMENTS" == *"--random"* || "$CLI_ARGUMENTS" == *"-r"*) && ("$CLI_ARGUMENTS" == *"--icsim"* || "$CLI_ARGUMENTS" == *"-i"*) ]]; then
  echo "[!] Error: either --random or --icsim can be chosen, not both! Please decide before coming back."
  print_help
  exit
fi

# Update Environment
if [[ "$CLI_ARGUMENTS" == *"--skip-update"* || "$CLI_ARGUMENTS" == *"-s"* ]]; then
  echo "[*] Update skipped."
else
  if sudo $PKG_MANAGER update >/dev/null; then
    echo "[+] Updated environment."
  else
    echo "[!] Update failed. You can skip update with --skip-update"
    exit
  fi
fi

# Check if all dependencies are meet
echo "[*] Checking if dependency libsdl2-dev is installed..."
if sudo apt-cache show libsdl2-dev >/dev/null; then
  echo "[*] Checking if dependency libsdl2-image-dev is installed..."
else
  echo "[!] Dependency libsdl2-dev is not installed. Trying to install it..."
  if sudo $PKG_MANAGER install libsdl2-dev; then
    echo "[+] Success. Continue..."
  else
    echo "[-] Unmeet dependencies. Please install them manually."
    exit
  fi
fi

if sudo apt-cache show libsdl2-image-dev >/dev/null; then
  echo "[+] Dependencies installed."
else
  echo "[!] Dependency libsdl2-image-dev is not installed. Trying to install it..."
  if sudo $PKG_MANAGER install libsdl2-image-dev; then
    echo "[+] Success. Continue..."
  else
    echo "[-] Unmeet dependencies. Please install them manually."
    exit
  fi
fi

# Check whether can-utils are available
echo "[*] Checking if can-utils are installed..."
if sudo apt-cache show can-utils >/dev/null; then
  echo "[+] can-utils are installed."
else
  echo "[!] can-utils are not installed. Trying to install them..."
  if sudo $PKG_MANAGER install can-utils; then
    echo "[+] Installed can-utils successfully. Going on..."
  else
    echo "[-] Failed to install can-utils! Please install them manually before coming back."
    exit
  fi
fi

# Enable kernel modules can & vcan
if sudo modprobe can; then
  echo -e "[*] Enabled can module."
else
  echo -e "[!] Error enabling can module! Exiting."
  exit
fi

if sudo modprobe vcan; then
  echo -e "[*] Enabled vcan module."
else
  echo -e "[!] Error enabling vcan module! Exiting."
  exit
fi

# Create and activate default interface
if sudo ip link add dev vcan0 type vcan > /dev/null; then
  echo -e "[*] Created interface vcan0."
else
  echo -e "[!] Error creating interface vcan0! (exists)"
fi

if sudo ip link set up vcan0; then
  echo -e "[*] Interface vcan0 is up."
else
  echo -e "[!] Could not set interface vcan0 up!"
fi

# Create and activate MITM interface
if sudo ip link add dev vcan1 type vcan > /dev/null; then
  echo -e "[*] Created interface vcan1."
else
  echo -e "[!] Error creating interface vcan1! (exists)"
fi

if sudo ip link set up vcan1; then
  echo -e "[*] Interface vcan1 is up."
else
  echo -e "[!] Could not set interface vcan1 up!"
fi

# Process command line arguments
# Generate random traffic without visualization
if [[ "$CLI_ARGUMENTS" == *"--random"* || "$CLI_ARGUMENTS" == *"-r"* ]]; then
  echo -e "[*] Started generating random CAN traffic on interface vcan0"
  echo -e "[*] Press CTRL+C to stop..."
  cangen vcan0 -g 4 -L 8 -D i
  exit
fi

# Start ICSim with random traffic and visualization
if [[ "$CLI_ARGUMENTS" == *"--icsim"* || "$CLI_ARGUMENTS" == *"-i"* ]]; then
  pushd $BASE_PATH/ICSim/ || (echo "Failed starting ICSim. Please check BASE_PATH" && exit)
  echo -e "[*] Starting instrument cluster simulation..."
  ./icsim -r vcan0 &
  ./controls -s !$ vcan0 &
  popd || exit
  exit
fi