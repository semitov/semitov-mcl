import time
from mcl_utils import MiddleLayer

ml = MiddleLayer()
ml.add_from("Pin", "machine")
ml.set_value("led", "Pin(10, Pin.OUT)")
val = 1
while True:
    val = not val
    led.value(val)
    time.sleep(2)

