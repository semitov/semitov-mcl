from mcl import Board
import time


def setup_network(ssid, password):
    import network

    ap = network.WLAN(network.WLAN.IF_AP)

    ap.active(False)

    ap.config(ssid=ssid, password=password, authmode=4)

    ap.active(True)

    return ap


with Board("COM4") as board:
    ap = board.def_function(setup_network)("ESP32 WiFi", "semitov-mlc")

    is_active = ap.active().get_value()
    ap_ifconfig = ap.ifconfig().get_value()
    ap_ssid = ap.config("ssid").get_value()

    print(f"AP active: {is_active}")
    print(f"ifconfig: {ap_ifconfig}")
    print(f"SSID: {ap_ssid}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ap.active(False)
