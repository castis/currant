# ultrasonic distance sensor

import time
# import numpy
import logging

from utility import StoppableThread
from utility import GPIO


logger = logging.getLogger('HCSR04')


class HCSR04():
    trigger = 22
    echo = 23
    altitude = 0
    history = []

    thread = None

    def __init__(self):
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, 0)

        def poll_events():
            while not self.thread.stopped():
                self.altitude = self.distance()
                time.sleep(0.2)

        self.thread = StoppableThread(
            target=poll_events,
            name="HCSR04"
        )
        self.thread.start()
        logger.info('up')

    def distance(self):
        start = 0
        end = 0

        # blast out a signal
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)

        # listen for the response
        while GPIO.input(self.echo) == GPIO.LOW:
            start = time.time()
        while GPIO.input(self.echo) == GPIO.HIGH:
            end = time.time()

        # distance in cm
        out = (end - start) * 17150

        # self.history.pop(0) # remove the item at the beginning
        # self.history.append(out) # tack a new value on the end

        # the signal is jumpy sometimes so smooth that shit

        # window = len(self.history)
        # weights = numpy.repeat(1.0, window) / window
        # out = numpy.convolve(self.history, weights, 'valid')

        # here we could use the accelerometers z axis to calculate the angle
        # of the craft and then measure `out` as the hypotenuse of a right triangle
        # and that would give us the distance from ground no matter our
        # position

        # return round(out)
        return out

    def down(self):
        self.thread.stop()
        self.thread.join()

        logger.info('down')
