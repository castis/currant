import collections
import itertools
import logging
import time
import os

import sensors
from utility import GPIO, PID

logger = logging.getLogger("vehicle")

try:
    mpu9250 = sensors.MPU9250()
except OSError as e:
    logger.critical("9dof board not found")
    exit(1)


class Magnetometer:
    initial_read = {"x": 0, "y": 0, "z": 0}
    last_good_read = {"x": 0, "y": 0, "z": 0}

    def __init__(self):
        # when starting up, get a snapshot of how the vehicle is positioned
        # relative to the magnetic field around it
        # this will be the basis of directional orientation
        # for the duration of the flight
        self.initial_read = self.read()

    def read(self):
        if reading := mpu9250.readMagnet():
            self.last_good_read = reading
        return self.last_good_read

    def deviation(self):
        #  how far the current reading is from the starting position
        return {
            "x": self.initial_read["x"] - self.last_good_read["x"],
            "y": self.last_good_read["y"] - self.initial_read["y"],
            "z": self.initial_read["z"] - self.last_good_read["z"],
        }


class Altimeter(object):
    history = []

    def __init__(self):
        self.sensor = sensors.HCSR04()

    def distance(self):
        # the front of the sensor is 2.9cm from the bottom of the feet
        self.history.insert(0, self.sensor.read() - 2.9)
        if len(self.history) > 30:
            self.history.pop()
        return sum(self.history) / len(self.history)


altimeter = Altimeter()
magnetometer = Magnetometer()


class Vehicle(object):
    control_pins = [19, 16, 26, 20]
    power_pins = [23, 27, 22, 17]
    motors = []
    temperature = 0
    # temperature = mpu9250.readTemperature()
    accelerometer = mpu9250.readAccel()
    gyro = mpu9250.readGyro()
    magnet = magnetometer.read()
    altitude = altimeter.distance()
    throttle = 0

    def __init__(self, args, timer, controller):
        self.motors = [
            Motor(control_pin=control, power_pin=power)
            for control, power in zip(self.control_pins, self.power_pins)
        ]
        self.timer = timer
        self.controller = controller

        self.pitch = PID(p=1.0, i=0.1, d=0)
        self.roll = PID(p=1.0, i=0.1, d=0)
        self.yaw = PID(p=1.0, i=0.002, d=0)

        logger.info("up")

    def update(self):
        self.accelerometer = mpu9250.readAccel()
        self.gyro = mpu9250.readGyro()
        self.magnet = magnetometer.read()
        self.deviation = magnetometer.deviation()
        self.altitude = altimeter.distance()

        # self.temperature = mpu9250.readTemperature()

        self.throttle = self.controller.buttons.lsy
        self.apply_throttle(self.throttle)

        pitch_delta = self.pitch(self.accelerometer["x"], self.timer.delta)
        self.apply_pitch(self.motors, pitch_delta)

        roll_delta = self.roll(self.accelerometer["y"], self.timer.delta)
        self.apply_roll(self.motors, roll_delta)

        # yaw_delta = self.yaw(
        #     self.deviation["y"],
        #     self.timer.delta
        # )
        # self.apply_yaw(self.motors, yaw_delta)

        for motor in self.motors:
            motor.tick()

    def apply_throttle(self, throttle):
        for motor in self.motors:
            motor.throttle = throttle

    def apply_pitch(self, motors, delta):
        motors[0].throttle -= delta * 100
        motors[1].throttle -= delta * 100
        motors[2].throttle += delta * 100
        motors[3].throttle += delta * 100

    def apply_roll(self, motors, delta):
        motors[0].throttle -= delta * 100
        motors[2].throttle -= delta * 100
        motors[1].throttle += delta * 100
        motors[3].throttle += delta * 100

    def apply_yaw(self, motors, delta):
        motors[0].throttle -= delta * 20
        motors[3].throttle -= delta * 20
        motors[1].throttle += delta * 20
        motors[2].throttle += delta * 20

    def down(self):
        self.apply_throttle(0)
        for motor in self.motors:
            motor.tick()
        GPIO.cleanup()
        logger.info("down")


# rescale(20, (0, 25), (12, 2)) == 4.0
# this says if a value is 20 on a scale from 0 to 25,
# what would that value be on a scale from 12 to 2?
# answer: 4
def rescale(val, in_: tuple, out_: tuple):
    v = (((val - in_[0]) * (out_[1] - out_[0])) / (in_[1] - in_[0])) + out_[0]
    return round(v, 2)


class Motor(object):
    """
    values below 20 produce what appears to be an alarming beep
    and values above like 90 dont produce much of a change
    so keep a range and adjust the throttle within it
    """

    # min_duty_cycle = 30
    # max_duty_cycle = 80

    duty_cycle_range = (30, 80)

    # duty_cycle_range = None
    throttle = 0
    throttle_range = (0, 100)
    dc = 0

    control_pin = None
    power_pin = None

    def __init__(self, control_pin=None, power_pin=None):
        GPIO.setup(control_pin, GPIO.OUT)
        # 500hz appears to generate the least amount of popping from the motor
        # as long as a prop is installed
        self.control_pin = GPIO.PWM(control_pin, 500)

        self.power_pin = power_pin
        GPIO.setup(self.power_pin, GPIO.OUT)

    def tick(self):
        self.control_pin.start(self.min_duty_cycle)
        self.dc = rescale(
            self.throttle, self.throttle_range, self.duty_cycle_range
        )

    def on(self):
        GPIO.output(self.power_pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.power_pin, GPIO.LOW)
