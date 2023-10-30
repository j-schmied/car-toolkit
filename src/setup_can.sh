#!/usr/bin/env bash


usage () {
	echo -e "usage: $0 <interface> <bitrate>"
    echo
    echo -e "options:"
    echo -e "  --fd:             Enables CAN-FD mode"
    echo
    echo -e "Valid interfaces: [v|sl]can[0-9]"
    echo -e "Valid bitrates: 10, 20, 50, 125, 250, 500, 800, 1000, 2000*, 5000*, 8000* (kbit/s)"
    echo
    echo -e "* CAN-FD only"
}

FD_MODE=0

if [[ "$*" == *"--fd"* ]]; then
	FD_MODE=1
	echo "[i] FD Mode enabled."
fi


if [[ $# -eq 1 || $# -gt 3 ]]; then
	usage
	exit 1
fi


main () {
	INTERFACE=$1
	declare -i BITRATE=$2
    
    if [[ ! "$INTERFACE" =~ ^(v|(sl))?can[0-9]+$ ]] ; then
    	echo -e "[!] Invalid interface"
        usage
        exit 1
    fi

	VALID_BITRATES=("10 20 50 125 250 500 800 1000 2000 5000 8000")
	
	if [[ " ${VALID_BITRATES[*]} " =~ " ${BITRATE} " ]] ; then
		if ifconfig $INTERFACE > /dev/null ; then
			if [[ "$FD_MODE" -eq "0" && $BITRATE -le 1000 ]]; then
				sudo ip link set $INTERFACE up type can bitrate $(($BITRATE * 1000))
			fi

			if [[ "$FD_MODE" -eq "1" ]]; then
				sudo ip link set $INTERFACE up type can bitrate $(($BITRATE * 1000)) sample-point 0.75 dbitrate $(($BITRATE * 0.8)) dsample-point 0.8 fd on
			fi
		else
			echo "[!] $INTERFACE: Interface unknown"
			usage
			exit 1
		fi
	else
		echo "[!] $BITRATE: Invalid bitrate."
		usage
		exit 1
	fi
}

main $1 $2