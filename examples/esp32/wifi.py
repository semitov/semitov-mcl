from mcl import Board
import time


def setup_network():
    import network
    import time

    ap = network.WLAN(network.WLAN.IF_AP)

    ap.active(False)
    time.sleep(1)

    essid = "WiFi ESP32"
    password = "pswdpswd"

    ap.config(essid=essid, password=password, authmode=4)

    ap.active(True)
    time.sleep(2)

    return ap


with Board("COM4") as board:
    ap = board.def_function(setup_network)()

    is_active = ap.active().get_value()
    ap_ifconfig = ap.ifconfig().get_value()
    ap_ssid = ap.config("ssid").get_value()

    print(f"AP active: {is_active}")
    print(f"IP conf: {ap_ifconfig}")
    print(f"SSID: {ap_ssid}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ap.active(False)
