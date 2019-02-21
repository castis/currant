#!/usr/bin/env python
import argparse
import logging
import os
import signal
import sys
import time
from functools import partial

import psutil
from engine import Chronograph, Display, Controller, Vehicle
from utility import Bluetoothctl

parser = argparse.ArgumentParser(description="Aviation!")

parser.add_argument(
    "-d", "--debug", action="store_true", dest="debug", help="Sets debug mode"
)
parser.add_argument(
    "-c",
    "--controller",
    action="store_true",
    dest="controller",
    help="Configure controller and exit",
)

args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger()


if args.controller:
    try:
        btctl = Bluetoothctl()
        seconds = 10

        logger.info(f"scanning for {seconds} seconds")
        btctl.start_scan()
        time.sleep(seconds)

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
            if not btctl.pair(device["mac_address"]):
                logger.error("could not pair %s" % device["name"])
                exit(1)
            logger.info("paired with %s" % device["name"])

            if not btctl.trust(device["mac_address"]):
                logger.error("could not trust %s" % device["name"])
            else:
                logger.info("trusted %s" % device["name"])

        logger.info("connecting to %s" % device["name"])
        if btctl.connect(device["mac_address"]):
            logger.info("connected")
        else:
            logger.error("could not connect")

    except KeyboardInterrupt as e:
        logger.info("quitting")

    exit(0)


class State(object):
    running = True
    debug = args.debug


state = State()
chronograph = Chronograph(state)
controller = Controller(state)
vehicle = Vehicle(state)
display = Display(state)


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
    # while the display is running as
    # it completely screws up the output
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
