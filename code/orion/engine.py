import logging
import time
import traceback

from .display import Display
from .vehicle import Vehicle, Motor
from .controller import Controller
from .chronograph import Chronograph
from utility import GPIO


logger = logging.getLogger('engine')

class Engine(object):
    vehicle = None
    controller = None
    chronograph = None
    display = None

    def __init__(self, args):
        logger.info('start')

        try:
            self.vehicle = Vehicle([27, 7, 21, 13])
            self.controller = Controller()
            self.chronograph = Chronograph()
            self.display = Display()

        except Exception as e:
            tb = traceback.format_exc()
            logger.info('exception caught\n%s' % tb)
            self.down()
            return

        logger.info('up')

        if not args.headless:
            # dramatic pause so we can see the log
            time.sleep(1)
            self.display.up()

        try:
            while True:
                self.chronograph.pre_loop()

                self.vehicle.tick(self.chronograph.delta, self.controller.map)
                self.display.tick(self)

                self.chronograph.post_loop()

        except KeyboardInterrupt:
            self.display.down()
            logger.info('caught ^C')

        except Exception as e:
            self.display.down()
            tb = traceback.format_exc()
            logger.info('exception caught\n%s' % tb)

        finally:
            self.down()

    def down(self):
        if self.vehicle:
            self.vehicle.down()

        if self.controller:
            self.controller.down()

        if self.chronograph:
            self.chronograph.down()

        logger.info('down')
