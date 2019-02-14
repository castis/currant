#!/usr/bin/env python
import argparse
import logging
import os
import signal
import sys
import time

import psutil
from utility.bluetoothctl import Bluetoothctl
from engine import Chronograph, Input, Vehicle

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


def restart(sig, frame):
    logger.info("restarting")
    try:
        p = psutil.Process(os.getpid())
        for handler in p.open_files() + p.connections():
            os.close(handler.fd)
    except Exception as e:
        logging.error(e)

    os.execl(sys.executable, sys.executable, *sys.argv)


signal.signal(signal.SIGUSR1, restart)


if args.controller:
    try:
        btctl = Bluetoothctl()
        seconds = 10

        logger.info(f"scanning for {seconds} seconds")
        btctl.start_scan()
        time.sleep(seconds)

        available = btctl.get_available_devices()
        paired = btctl.get_paired_devices()
        device = None

        while device == None:
            print("select a device:")
            for i, d in enumerate(available):
                print("%s. %s" % (i + 1, d["name"]))
            try:
                selected = int(input("number: ")) - 1
                device = available[selected]
            except (ValueError, IndexError) as e:
                logger.error("bad choice")

        if not device in paired:
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
    motor_pins = [19, 16, 26, 20]


state = State()
chronograph = Chronograph(state)
# input = Input(state)
vehicle = Vehicle(state)

try:
    while True:
        # input.update(state)
        vehicle.update(state)
        chronograph.update(state)

except (Exception, KeyboardInterrupt) as e:
    logger.info("quitting")

finally:
    vehicle.down()
    # input.down()
    chronograph.down()
