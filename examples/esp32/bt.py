from mcl import Board
import time

with Board("COM4") as board:

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

    setup_ble_remote = board.def_function(setup_ble)
    ble_device = setup_ble_remote("ESP32 BT")
    print(ble_device.hex())

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupt")
