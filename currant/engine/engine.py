import logging
import sys
import pickle


from .display import Display
from .vehicle import Vehicle
from .input import Input
from .output import Output
from .chronograph import Chronograph


logger = logging.getLogger("engine")


class Engine(object):
    output = None
    running = False

    def __init__(self, args):
        self.chronograph = Chronograph()
        self.input = Input()
        self.vehicle = Vehicle(motor_pins=[19, 16, 26, 20])
        # self.display = Display()

        if args.debug:
            self.output = Output()

        if not args.headless:
            self.display.up()

    async def run(self):
        self.running = True
        try:
            while True:
                self.input.update()
                self.vehicle.update(self)
                # self.display.update(self)
                self.chronograph.update()
                # if self.output:
                #     self.output.tick(self)

                # if self.running and self.input.state["KILL"] == True:
                    # self.stop()
                    # exit()
        except:
            # if self.display:
                # self.display.down()
            raise

    def reload(self, engine):
        pass
        # file = '/tmp/flight_controller'
        # with open(file, 'wb') as f:
        #     pickle.dump(self.input, f)
        # with open(file, 'rb') as f:
        #     self.input = pickle.load(f)
        # self.input = engine.Input(self.input.device, self.input.state)

    def stop(self):
        self.running = False
        # self.display.down()
        self.vehicle.down()
        self.input.down()
        self.chronograph.down()
        # if self.output:
            # self.output.down()
