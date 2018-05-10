import logging
import sys


from .display import Display
from .vehicle import Vehicle
from .input import Input
from .chronograph import Chronograph


logger = logging.getLogger('engine')


class Engine(object):

    def __init__(self, args):
        self.chronograph = Chronograph()
        self.input = Input()
        self.vehicle = Vehicle(motor_pins=[19, 16, 26, 20])
        self.display = Display()

        if not args.headless:
            self.display.up()

    async def run(self):
        while True:
            self.chronograph.pre_loop()

            self.input.update(self)
            self.vehicle.update(self)
            self.display.update(self)

            await self.chronograph.post_loop()

    def reload(self):
        pass

    def stop(self):
        self.display.down()
        self.vehicle.down()
        self.input.down()
        self.chronograph.down()
