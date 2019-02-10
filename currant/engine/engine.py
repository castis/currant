import logging

from .vehicle import Vehicle
from .input import Input
from .chronograph import Chronograph


logger = logging.getLogger("engine")


class Engine(object):
    def __init__(self, args):
        self.chronograph = Chronograph()
        self.input = Input()
        self.vehicle = Vehicle(motor_pins=[19, 16, 26, 20])

    async def start(self):
        try:
            while True:
                self.input.update()
                self.vehicle.update(self)
                await self.chronograph.update()

        except Exception as e:
            logger.error(e.getMessage())
            # raise

    def stop(self):
        self.vehicle.down()
        self.input.down()
        self.chronograph.down()
