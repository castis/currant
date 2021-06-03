import logging
from time import sleep

from evdev import InputDevice, categorize, ecodes
from utility import Bluetoothctl

logger = logging.getLogger("controller")


class Controller(object):
    running = False

    device_file = "/dev/input/event0"
    input_device = None
    raw = {}

    class buttons:
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

    def __init__(self, args):
        if args.setup_bt:
            self.setup_bluetooth()

        self.running = self.up()

        if not self.running:
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

        if device in btctl.get_paired_devices():
            logger.info("already paired with %s" % device["name"])
        else:
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

        if device in btctl.get_paired_devices():
            connected = btctl.connect(device["mac_address"])
            logger.info("%s to %s" % ("connected" if connected else "could not connect", device["name"]))

    def up(self):
        try:
            self.input_device = InputDevice(self.device_file)
            logger.info("up")
        except FileNotFoundError:
            return False
        return True

    def get(self, button, default=False):
        return getattr(self.buttons, button, default)

    def update(self):
        if self.input_device:
            try:
                for event in self.input_device.read():
                    self.receive_event(event)
            except BlockingIOError:
                pass
            except OSError:
                logger.error("controller was unplugged")
                self.down()
        else:
            self.running = self.up()

    # mapping for an 8bitdo sn30 pro
    def receive_event(self, event):
        self.raw[event.code] = event.value

        # print(categorize(event))
        # print(event.value)
        logger.debug(event.value)

        if event.code == 305:  # east
            self.buttons.a = event.value == 1

        elif event.code == 304:  # south
            self.buttons.b = event.value == 1

        elif event.code == 307:  # north
            self.buttons.x = event.value == 1

        elif event.code == 306:  # west
            self.buttons.y = event.value == 1

        elif event.code == 308:
            self.buttons.l1 = event.value == 1

        elif event.code == 309:
            self.buttons.r1 = event.value == 1

        elif event.code == ecodes.ABS_Z:
            self.buttons.l2 = event.value > 0

        elif event.code == ecodes.ABS_RZ:
            self.buttons.r2 = event.value > 0

        elif event.code == 312:
            self.buttons.l3 = event.value > 0

        elif event.code == 313:
            self.buttons.r3 = event.value > 0

        elif event.code == 310:
            self.buttons.select = event.value == 1

        elif event.code == 311:
            self.buttons.start = event.value == 1

        elif event.code == ecodes.ABS_RY:
            self.buttons.rsy = -(event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_RX:
            self.buttons.rsx = (event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_Y:
            self.buttons.lsy = -(event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_X and event.type == 3:
            self.buttons.lsx = (event.value - 32768) / 327.68

        elif event.code == ecodes.ABS_HAT0Y:
            self.buttons.up = event.value == -1
            self.buttons.down = event.value == 1

        elif event.code == ecodes.ABS_HAT0X:
            self.buttons.left = event.value == -1
            self.buttons.right = event.value == 1

        elif event.code == ecodes.KEY_MENU:
            self.buttons.menu = event.value > 0
            if self.buttons.menu:
                self.running = False

    def down(self):
        if self.input_device:
            self.input_device.close()
            self.input_device = None
        self.running = False
        logger.info("down")
