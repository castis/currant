from .engine import Engine
from .display import Display
from .vehicle import Vehicle, Motor
from .controller import Controller
from .chronograph import Chronograph


# just an idea
class FlightComponent(object):
    def up(self):
        pass

    def tick(self, time_delta):
        pass

    def down(self):
        pass
