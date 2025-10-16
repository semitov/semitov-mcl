from mcl import Board
import time


def setup_network():
    import network

    ap_if = network.WLAN(network.WLAN.IF_AP)
    return ap_if


with Board("COM4") as board:
    ap = board.def_function(setup_network)()
    ap.active(True)
    essid = "WiFi ESP32"
    password = "pswd"
    ap.config(essid, password)

    print(f"Active: {ap.ifconfig()}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted")
