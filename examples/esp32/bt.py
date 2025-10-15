from mcl import Board
import time


def setup_ble(device_name):
    import bluetooth

    ble = bluetooth.BLE()
    ble.active(True)
    ble.config("mac")
    adv_data = (
        bytes([0x02, 0x01, 0x06, len(device_name) + 1, 0x09]) + device_name.encode()
    )
    ble.gap_advertise(100000, adv_data)

    return ble


with Board("COM4") as board:
    ble = board.def_function(setup_ble)()

    print(ble.name)
    res = board.execute_raw(f"print({ble.name})", echo=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted")
