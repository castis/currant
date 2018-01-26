# ultrasonic sensor
import time
import numpy

from utility import GPIO


class HCSR04():
    TRIG = 23
    ECHO = 24

    def __init__(self):
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        GPIO.output(self.TRIG, 0)
        self.history = list(range(100))
        # self.history = deque(maxlen=150)

    def distance(self):
        start, end = 0, 0

        # blast out a signal
        GPIO.output(self.TRIG, 1)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, 0)

        # listen for the response
        while GPIO.input(self.ECHO) == 0:
            start = time.time()
        while GPIO.input(self.ECHO) == 1:
            end = time.time()

        # distance in cm
        out = (end - start) * 17150

        self.history.pop(0) # remove the item at the beginning
        self.history.append(out) # tack a new value on the end

        # the signal is jumpy sometimes so smooth that shit

        window = len(self.history)
        weights = numpy.repeat(1.0, window) / window
        out = numpy.convolve(self.history, weights, 'valid')

        return round(out)
