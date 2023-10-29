"""
    Scapy config for automotive pentest 
"""
from scapy.main import load_layer, load_contrib
from scapy.config import conf

def init_can(use_pycan: bool = False):
    if use_pycan:
        import can

    load_layer("can")
    conf.contribs['CANSocket'] = {'use-python-can': use_pycan}
    load_contrib("cansocket")


def init_uds():
    load_contrib('automotive.uds')
    conf.contribs['ISOTP'] = {'use-can-isotp-kernel-module': True}
    load_contrib('isotp')


def init_obd():
    import obd
    conf.contribs['ISOTP'] = {'use-can-isotp-kernel-module': True}
    load_contrib('isotp')
    load_contrib('automotive.obd.obd')


def init_xcp():
    load_contrib('automotive.xcp.xcp')


def setup_can():
    CSOCK = CANSocket("can0")
    return CSOCK


def setup_vcans() -> tuple:
    SOCK1 = CANSocket("vcan0")
    SOCK2 = CANSocket("vcan1")
    return SOCK1, SOCK2


def setup_uds(did, sid):
    USOCK = ISOTPNativeSocket(iface="can0", tx_id=did, rx_id=sid, basecls=UDS)
    return USOCK


def setup_obd(did, sid):
    OSOCK = ISOTPNativeSocket("can0", tx_id=did, rx_id=sid, padding=True, basecls=OBD)
    return OSOCK


def setup_xcp():
    XSOCK = CANSocket(channel="can0", basecls=XCPOnCAN)
    return XSOCK


def xcp_send_unlock():
    XSOCK = setup_xcp()
    unlock_pkt = XCPOnCAN(identifier=0x70b) / CTORequest() / Unlock()
    XSOCK.sr1(unlock_pkt)