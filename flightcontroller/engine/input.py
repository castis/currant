import logging
from utility import StoppableThread
from evdev import categorize, ecodes, InputDevice

logger = logging.getLogger('input')


class Input(object):
    A = False
    B = False
    X = False
    Y = False
    LT = 0
    RT = 0
    LB = False
    RB = False
    LS = False
    RS = False
    RX = 0
    RY = 0

    _device = None
    _raw = {}

    def __init__(self):
        try:
            self._device = InputDevice('/dev/input/event0')
        except FileNotFoundError:
            logger.error('cant open input device')
            exit(1)

        logger.info('up')

    def __repr__(self):
        return f'''RT:{self.RT}'''

    def update(self, engine):
        try:
            for event in self._device.read():
                self.receive_event(event)
        except BlockingIOError:
            pass

    def receive_event(self, event):
        self._raw[event.code] = event.value

        if event.code == ecodes.BTN_A:
            self.A = event.value == 1
        elif event.code == ecodes.BTN_B:
            self.B = event.value == 1
        elif event.code == ecodes.BTN_X:
            self.X = event.value == 1
        elif event.code == ecodes.BTN_Y:
            self.Y = event.value == 1

        elif event.code == ecodes.ABS_BRAKE:
            self.LT = event.value
        elif event.code == ecodes.ABS_GAS:
            self.RT = event.value

        elif event.code == ecodes.BTN_TL:
            self.LB = event.value == 1
        elif event.code == ecodes.BTN_TR:
            self.RB = event.value == 1

        elif event.code == ecodes.BTN_THUMBL:
            self.LS = event.value == 1
        elif event.code == ecodes.BTN_THUMBR:
            self.RS = event.value == 1

        elif event.code == ecodes.ABS_RX:
            self.RX = event.value
        elif event.code == ecodes.ABS_RY:
            self.RY = event.value

    def down(self):
        self._device.close()
        logger.info('down')

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
