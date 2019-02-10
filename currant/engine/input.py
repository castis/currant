import logging
from evdev import categorize, ecodes, InputDevice

logger = logging.getLogger("input")


class Input(object):
    state = {
        "A": False,
        "B": False,
        "X": False,
        "Y": False,
        # "L1": False,
        # "R1": False,
        # "L2": False,
        # "R2": False,
        # "L3": False,
        # "R3": False,
        # "LX": 0,
        # "LY": 0,
        # "RX": 0,
        # "RY": 0,
        # "KILL": 0,
    }
    device = None
    raw = {}

    def __init__(self):
        # try:
        #     self.device = InputDevice("/dev/input/event0")
        # except FileNotFoundError:
        #     logger.error("cant open input device")
        #     exit(1)
        logger.info("up")

    # dont do this here, display all the buttons in Display()
    # def __repr__(self):
    #     return "LT: RT:%s" % (self.state["RT"],)

    def get(self, button, default=False):
        return self.state.get(button, default)

    def update(self):
        # print("\rtest")
        pass
        # try:
        #     for event in self.device.read():
        #         self.receive_event(event)
        # except BlockingIOError:
        #     pass

    def receive_event(self, event):
        self.raw[event.code] = event.value

        if event.code == ecodes.BTN_A:
            self.state["A"] = event.value == 1
        elif event.code == ecodes.BTN_B:
            self.state["B"] = event.value == 1
        elif event.code == ecodes.BTN_X:
            self.state["X"] = event.value == 1
        elif event.code == ecodes.BTN_Y:
            self.state["Y"] = event.value == 1

        elif event.code == ecodes.ABS_BRAKE:
            self.state["LT"] = event.value
        elif event.code == ecodes.ABS_GAS:
            self.state["RT"] = event.value

        elif event.code == ecodes.BTN_TL:
            self.state["LB"] = event.value == 1
        elif event.code == ecodes.BTN_TR:
            self.state["RB"] = event.value == 1

        elif event.code == ecodes.BTN_THUMBL:
            self.state["LS"] = event.value == 1
        elif event.code == ecodes.BTN_THUMBR:
            self.state["RS"] = event.value == 1

        elif event.code == ecodes.ABS_X:
            self.state["LX"] = event.value
        elif event.code == ecodes.ABS_Y:
            self.state["LY"] = event.value

        elif event.code == ecodes.ABS_RX:
            self.state["RX"] = event.value
        elif event.code == ecodes.ABS_RY:
            self.state["RY"] = event.value

        elif event.code == ecodes.BTN_MODE:
            self.state["KILL"] = event.value == 1

    def down(self):
        # self.device.close()
        # self.device = None
        logger.info("down")


# {
#     ('EV_KEY', 1L): [
#         ('BTN_BASE', 294L),
#         ('BTN_BASE2', 295L),
#         ('BTN_BASE3', 296L),
#         ('BTN_BASE4', 297L),
#         (['BTN_A', 'BTN_GAMEPAD', 'BTN_SOUTH'], 304L),
#         (['BTN_B', 'BTN_EAST'], 305L),
#         (['BTN_NORTH', 'BTN_X'], 307L),
#         (['BTN_WEST', 'BTN_Y'], 308L),
#         ('BTN_TL', 310L),
#         ('BTN_TR', 311L),
#         ('BTN_SELECT', 314L),
#         ('BTN_START', 315L),
#         ('BTN_MODE', 316L),
#         ('BTN_THUMBL', 317L),
#         ('BTN_THUMBR', 318L)
#     ],
#     ('EV_ABS', 3L): [
#         (('ABS_X', 0L), AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
#         (('ABS_Y', 1L), AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
#         (('ABS_RX', 3L), AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
#         (('ABS_RY', 4L), AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
#         (('ABS_GAS', 9L), AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
#         (('ABS_BRAKE', 10L), AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0))
#     ],
#     ('EV_SYN', 0L): [('SYN_REPORT', 0L), ('SYN_CONFIG', 1L), ('SYN_DROPPED', 3L)]
# }
