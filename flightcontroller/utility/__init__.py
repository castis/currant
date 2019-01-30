import logging


from .pid import *
from .StoppableThread import StoppableThread

try:
    import RPi.GPIO as GPIO
except ImportError:
    logger = logging.getLogger("utility")
    logger.info("loading stub GPIO library")
    from .RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
