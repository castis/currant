import logging
from time import sleep

from utility.bluetoothctl import Bluetoothctl
from evdev import InputDevice, categorize, ecodes


logger = logging.getLogger("input")


class Input(object):
    state = {
        "a": False,
        "b": False,
        "x": False,
        "y": False,
        "l1": False,
        "r1": False,
        "l2": False,
        "r2": False,
        "l3": False,
        "r3": False,
        "start": False,
        "select": False,
        # "RX": 0,
        # "RY": 0,
        # "KILL": 0,
    }
    device = None
    raw = {}

    def __init__(self, state):
        try:
            name = "/dev/input/event0"
            self.device = InputDevice(name)
            logger.info("up")
        except FileNotFoundError:
            logger.error(f"cannot open {name}")

    # dont do this here, display all the buttons in Display()
    # def __repr__(self):
    #     return "LT: RT:%s" % (self.state["RT"],)

    def get(self, button, default=False):
        return self.state.get(button, default)

    def update(self, state):
        if self.device:
            try:
                for event in self.device.read():
                    self.receive_event(event)
            except BlockingIOError:
                pass

    # mapping for an 8bitdo sn30 pro
    def receive_event(self, event):
        self.raw[event.code] = event.value

        # print(categorize(event))
        # print(event.value)

        if event.code == 305:  # east
            self.state["a"] = event.value == 1

        elif event.code == 304:  # south
            self.state["b"] = event.value == 1

        elif event.code == 307:  # north
            self.state["x"] = event.value == 1

        elif event.code == 306:  # west
            self.state["y"] = event.value == 1

        elif event.code == 308:
            self.state["l1"] = event.value == 1

        elif event.code == 309:
            self.state["r1"] = event.value == 1

        elif event.code == ecodes.ABS_Z:
            self.state["l2"] = event.value > 0

        elif event.code == ecodes.ABS_RZ:
            self.state["r2"] = event.value > 0

        elif event.code == 312:
            self.state["l3"] = event.value > 0

        elif event.code == 313:
            self.state["r3"] = event.value > 0

        elif event.code == 310:
            self.state["select"] = event.value == 1

        elif event.code == 311:
            self.state["start"] = event.value == 1

        # elif event.code == ecodes.ABS_HAT0Y:
        #     self.state

        # print(self.state)

        # elif event.code == ecodes.BTN_THUMBL:
        #     self.state["LS"] = event.value == 1
        # elif event.code == ecodes.BTN_THUMBR:
        #     self.state["RS"] = event.value == 1

        # elif event.code == ecodes.ABS_X:
        #     self.state["LX"] = event.value
        # elif event.code == ecodes.ABS_Y:
        #     self.state["LY"] = event.value

        # elif event.code == ecodes.ABS_RX:
        #     self.state["RX"] = event.value
        # elif event.code == ecodes.ABS_RY:
        #     self.state["RY"] = event.value

        # elif event.code == ecodes.BTN_MODE:
        #     self.state["KILL"] = event.value == 1

    def down(self):
        if self.device:
            self.device.close()
            self.device = None
        logger.info("down")
