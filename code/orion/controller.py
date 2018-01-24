import logging
import time
from utility import StoppableThread
from evdev import categorize, ecodes, InputDevice

logger = logging.getLogger('controller')


class Controller:
    def __init__(self):
        self.map = {
            'A': False,
            'B': False,
            'X': False,
            'Y': False,
            'RT': 0,
            'RS': False,
            'LT': 0,
        }
        self.raw = {}

        try:
            device = InputDevice('/dev/input/event0')
        except FileNotFoundError:
            logger.error('cant open input device')
            exit(1)

        def poll_events(device):
            while not self.thread.stopped():
                try:
                    for event in device.read():
                        self.receive_event(event)
                except BlockingIOError:
                    time.sleep(0.1)
            return

        self.thread = StoppableThread(
            target=poll_events,
            args=(device,),
            name="Controller"
        )
        self.thread.start()
        logger.info('listening')

    def receive_event(self, event):
        self.raw[event.code] = event.value
        if event.code == ecodes.BTN_A:
            self.map['A'] = event.value == 1
        if event.code == ecodes.BTN_B:
            self.map['B'] = event.value == 1
        if event.code == ecodes.BTN_X:
            self.map['X'] = event.value == 1
        if event.code == ecodes.BTN_Y:
            self.map['Y'] = event.value == 1
        if event.code == ecodes.ABS_RZ:
            self.map['RT'] = event.value
        # if event.code == ecodes.ABS_RZ:
        #     self.map['LT'] = event.value
        if event.code == ecodes.BTN_THUMBR:
            self.map['RS'] = event.value == 1

    def shutdown(self):
        logger.info('shutdown')

        self.thread.stop()
        self.thread.join()

        logger.info('halted')

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
