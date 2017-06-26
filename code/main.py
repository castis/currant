from time import sleep
from pprint import pprint

import logging

try:
    import RPi.GPIO as GPIO
except ImportError:
    from MockRPi import GPIO


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger()


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Motor():
    max_duty_cycle = 90
    min_duty_cycle = 10
    duty_cycle_range = None

    pin = None

    def __init__(self, pin=None):
        # values below 20 produce what appears to be an alarming beep
        # and values above like 90 dont produce much of a change
        # so keep a range and adjust the throttle within it
        self.duty_cycle_range = self.max_duty_cycle - self.min_duty_cycle

        GPIO.setup(pin, GPIO.OUT)

        # 500 appears to reduce the amount of popping from the motor
        # as long as a prop is installed
        self.pin = GPIO.PWM(pin, 500)
        self.pin.start(0) # duty cycle

    def set_throttle(self, percentage):
        try:
            percentage = int(percentage)
            if max(min(100, percentage), 0) != percentage:
                raise ValueError
        except ValueError:
            # fail shut
            percentage = 0

        duty_cycle = self.min_duty_cycle + (percentage * self.duty_cycle_range / 100)
        self.pin.ChangeDutyCycle(duty_cycle)


class Vehicle():
    # front
    #cw ccw
    # 0  2
    #  \/
    #  /\
    # 3  1
    #ccw cw
    # rear
    def __init__(self, motors):
        self.motors = motors

    def set_throttle(self, throttle):
        for motor in self.motors:
            motor.set_throttle(throttle)

    def shutdown(self):
        self.set_throttle(0)
        time.sleep(1)
        GPIO.cleanup()
        print(" shutdown")


try:
    vehicle = Vehicle([
        Motor(pin=21),
        Motor(pin=19),
        Motor(pin=26),
        Motor(pin=20),
    ])

    while True:
        throttle = input("set throttle: ")
        vehicle.set_throttle(throttle)

except KeyboardInterrupt:
    vehicle.shutdown()
