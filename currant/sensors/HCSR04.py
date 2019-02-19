# ultrasonic distance sensor

from time import sleep, time
# import numpy
import logging

from utility import GPIO


logger = logging.getLogger('HCSR04')


class HCSR04():
    trigger = 22
    echo = 23
    altitude = 0
    history = []

    thread = None

    # max amount of loops to wait for a response
    timeout_threshold = 300
    # timeouts = 0

    def __init__(self):
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, 0)
        self.last_good_read = 0

        logger.info('up')

    def distance(self):
        # blast out a signal
        GPIO.output(self.trigger, GPIO.HIGH)
        sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        # listen for the response
        i = 0
        start = 0
        while i < self.timeout_threshold and GPIO.input(self.echo) == GPIO.LOW:
            start = time()
            i = i + 1

        end = 0
        while i < self.timeout_threshold and GPIO.input(self.echo) == GPIO.HIGH:
            end = time()
            i = i + 1

        if i >= self.timeout_threshold:
            # self.timeouts = self.timeouts + 1
            return self.last_good_read

        # distance in cm
        self.last_good_read = (end - start) * 17150

        # here we could use the accelerometers z axis to calculate the angle
        # of the craft and then measure `out` as the hypotenuse of a right triangle
        # and that would give us the distance from ground no matter our attitude

        return self.last_good_read

    def down(self):
        logger.info('down')
