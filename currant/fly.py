#!/usr/bin/env python
import argparse
import datetime
import logging
import os
import signal
import sys
import time
import pdb
from functools import partial

import psutil
from engine import Controller, Display, Timer, Vehicle

logger = logging.getLogger()


parser = argparse.ArgumentParser(description="Aviation!")

parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    dest="debug",
    help="Disables curses front end and custom logger",
)
parser.add_argument(
    "--disable-display",
    action="store_false",
    dest="display_enabled",
    help="Disable the curses frontend",
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


log = [""] * 6


class Handler(logging.Handler):
    def __init__(self, history):
        logging.Handler.__init__(self)
        self.history = history

    def emit(self, record):
        current_time = time.strftime("%H:%M:%S", time.gmtime())
        message = f"{current_time} - {record.name} - {record.msg}"
        print(message)
        self.history.insert(0, message)
        self.history.pop()


if args.display_enabled:
    for h in list(logger.handlers):
        logger.removeHandler(h)
    logger.addHandler(Handler(log))


timer = Timer(args)
controller = Controller(args)
vehicle = Vehicle(args, timer, controller)
display = Display(args, timer, controller, vehicle)


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


running = True
stored_exception = None
try:
    while running:
        if args.debug:
            pdb.set_trace()
        controller.update()
        vehicle.update()
        timer.update()
        display.update()

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
    timer.down()

    if stored_exception:
        raise stored_exception
