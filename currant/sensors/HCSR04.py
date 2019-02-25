# ultrasonic distance sensor

import logging
from time import sleep, time

from utility import GPIO

logger = logging.getLogger("HCSR04")


class HCSR04:
    trigger = 22
    echo = 23
    altitude = 0

    # max amount of loops to wait for a response
    timeout_threshold = 300

    def __init__(self):
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, 0)
        self.last_good_read = 0

        logger.info("up")

    def read(self):
        # blast out a signal
        GPIO.output(self.trigger, GPIO.HIGH)
        sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        # listen for the response
        i = 0
        start = time()
        while i < self.timeout_threshold and GPIO.input(self.echo) == GPIO.LOW:
            start = time()
            i = i + 1

        end = time()
        while i < self.timeout_threshold and GPIO.input(self.echo) == GPIO.HIGH:
            end = time()
            i = i + 1

        if i < self.timeout_threshold:
            # distance in cm
            self.last_good_read = (end - start) * 17150
            # if we assume last_good_read is the hypotenuse of a right
            # triangle, we could get the angle of the vehicle from the
            # accelerometer and we'll have altitude regardless of angle

        return self.last_good_read

    def down(self):
        logger.info("down")
