# ultrasonic sensor
import time
import numpy

from utility import GPIO


class HCSR04():
    trigger = 22
    echo = 23

    def __init__(self):
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, 0)
        # self.history = list(range(100))
        # self.history = deque(maxlen=150)

    def altitude(self):
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
        # and that would give us the distance from ground no matter our position


        # return round(out)
        return out