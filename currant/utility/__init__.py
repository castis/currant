import logging

from .bluetoothctl import Bluetoothctl
from .pid import *

try:
    import RPi.GPIO as GPIO
except ImportError:
    logger = logging.getLogger("utility")
    logger.info("loading stub GPIO library")
    from .RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
