import logging
from time import sleep

from evdev import InputDevice, categorize, ecodes
from utility import Bluetoothctl

logger = logging.getLogger("controller")


class Controller(object):
    device_file = "/dev/input/event0"
    input_device = None
    raw = {}

    class State:
        a = False
        b = False
        x = False
        y = False
        l1 = False
        r1 = False
        l2 = False
        r2 = False
        l3 = False
        r3 = False
        start = False
        select = False
        rsy = 0
        rsx = 0
        lsy = 0
        lsx = 0
        up = False
        down = False
        left = False
        right = False
        menu = False

        def get(*args, **kwargs):
            return getattr(*args, **kwargs)

    def __init__(self, state):
        state.controller = self.State

        if state.args.setup_bt:
            self.setup_bluetooth()

        self.State.running = self.up()

        if not self.State.running:
            logger.error("could not open device file")

    def setup_bluetooth(self):
        btctl = Bluetoothctl()
        seconds = 5

        logger.info(f"scanning for {seconds} seconds")
        btctl.start_scan()
        sleep(seconds)

        device = None
        while device == None:
            available = btctl.get_available_devices()
            print("select a device:\n0. reload list")
            for i, d in enumerate(available):
                print("%s. %s" % (i + 1, d["name"]))
            try:
                selection = int(input("number: ")) - 1
                device = available[selection]
            except (ValueError, IndexError) as e:
                logger.error("no device selected, reloading list")

        btctl.stop_scan()

        if not device in btctl.get_paired_devices():
            logger.info("pairing %s" % device["name"])
            if btctl.pair(device["mac_address"]):
                logger.info("paired")
                # auto-connect when seen in the future
                if btctl.trust(device["mac_address"]):
                    logger.info("and trusted")
                else:
                    logger.error("but could not trust %s" % device["name"])
            else:
                logger.error("could not pair")
        else:
            logger.info("already paired with %s" % device["name"])

        if device in btctl.get_paired_devices():
            logger.info("connecting to %s" % device["name"])
            if btctl.connect(device["mac_address"]):
                logger.info("connected")
            else:
                logger.error("could not connect")

    def up(self):
        try:
            self.input_device = InputDevice(self.device_file)
            logger.info("up")
        except FileNotFoundError:
            return False
        return True

    def get(self, button, default=False):
        return getattr(self.State, button, default)

    def update(self, state):
        if self.input_device:
            try:
                for event in self.input_device.read():
                    self.receive_event(event, state)
            except BlockingIOError:
                pass
            except OSError:
                logger.error("controller was unplugged")
                self.down()
        else:
            self.State.running = self.up()

    # mapping for an 8bitdo sn30 pro
    def receive_event(self, event, state):
        self.raw[event.code] = event.value

        # print(categorize(event))
        # print(event.value)

        if event.code == 305:  # east
            self.State.a = event.value == 1

        elif event.code == 304:  # south
            self.State.b = event.value == 1

        elif event.code == 307:  # north
            self.State.x = event.value == 1

        elif event.code == 306:  # west
            self.State.y = event.value == 1

        elif event.code == 308:
            self.State.l1 = event.value == 1

        elif event.code == 309:
            self.State.r1 = event.value == 1

        elif event.code == ecodes.ABS_Z:
            self.State.l2 = event.value > 0

        elif event.code == ecodes.ABS_RZ:
            self.State.r2 = event.value > 0

        elif event.code == 312:
            self.State.l3 = event.value > 0

        elif event.code == 313:
            self.State.r3 = event.value > 0

        elif event.code == 310:
            self.State.select = event.value == 1

        elif event.code == 311:
            self.State.start = event.value == 1

        elif event.code == ecodes.ABS_RY:
            self.State.rsy = -(event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_RX:
            self.State.rsx = (event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_Y:
            self.State.lsy = -(event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_X and event.type == 3:
            self.State.lsx = (event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_HAT0Y:
            self.State.up = event.value == -1
            self.State.down = event.value == 1

        elif event.code == ecodes.ABS_HAT0X:
            self.State.left = event.value == -1
            self.State.right = event.value == 1

        elif event.code == ecodes.KEY_MENU:
            self.State.menu = event.value > 0
            if self.State.menu:
                state.running = False

    def down(self):
        if self.input_device:
            self.input_device.close()
            self.input_device = None
        self.State.running = False
        logger.info("down")
