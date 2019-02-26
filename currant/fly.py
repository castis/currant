#!/usr/bin/env python
import argparse
import datetime
import logging
import os
import signal
import sys
import time
from functools import partial

import psutil
from engine import Chronograph, Controller, Display, Vehicle
from utility import Bluetoothctl

parser = argparse.ArgumentParser(description="Aviation!")

parser.add_argument(
    "-d", "--debug", action="store_true", dest="debug", help="Sets debug mode"
)
parser.add_argument(
    "--setup-bt",
    action="store_true",
    dest="setup_bt",
    help="Setup bluetooth controller",
)

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)


class State(object):
    running = True
    log = []

    def __init__(self, args):
        self.args = args

state = State(args)


class Handler(logging.Handler):
    def __init__(self, history):
        logging.Handler.__init__(self)
        self.history = history

    def emit(self, record):
        current_time = time.strftime("%H:%M:%S", time.gmtime())
        message = f"{current_time} - {record.name} - {record.msg}"

        print(message)
        self.history.insert(0, message)
        if len(self.history) > 6:
            self.history.pop()

logger = logging.getLogger()

for h in list(logger.handlers):
    logger.removeHandler(h)

logger.addHandler(Handler(state.log))


chronograph = Chronograph(state)
controller = Controller(state)
vehicle = Vehicle(state)
display = Display(state)

# todo: pass in state instead of display and refuse to restart if altitude > 0
def restart(display, sig, frame):
    if display:
        display.down()
    logger.info("restarting...")

    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    os.execl(sys.executable, sys.executable, *sys.argv)

signal.signal(signal.SIGUSR1, partial(restart, display))


stored_exception = None
try:
    while state.running:
        controller.update(state)
        vehicle.update(state)
        chronograph.update(state)
        display.update(state)

except Exception as e:
    # we dont want to throw an exception
    # while the display is running because
    # it completely screws up the terminal
    if display:
        stored_exception = e
    else:
        raise

except KeyboardInterrupt:
    pass

finally:
    display.down()
    vehicle.down()
    controller.down()
    chronograph.down()

    if stored_exception:
        raise stored_exception
