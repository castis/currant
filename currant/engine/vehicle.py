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
        reading = mpu9250.readMagnet()
        if reading:
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
        self.history.insert(0, self.read())
        if len(self.history) > 30:
            self.history.pop()
        return sum(self.history) / len(self.history)

    def read(self):
        # front of sensor is mounted this
        # far from bottom of vehicle
        return self.sensor.read() - 2.90


altimeter = Altimeter()
magnetometer = Magnetometer()


class Vehicle(object):

    class State:
        control_pins = [19, 16, 26, 20]
        power_pins = [17, 27, 22, 23]
        motors = []
        temperature = 0
        # temperature = mpu9250.readTemperature()
        accelerometer = mpu9250.readAccel()
        gyro = mpu9250.readGyro()
        magnet = magnetometer.read()
        altitude = altimeter.distance()
        throttle = 0

    def __init__(self, state):
        state.vehicle = self.State
        state.vehicle.motors = [
            Motor(control_pin=control, power_pin=power)
            for control, power in zip(state.vehicle.control_pins, state.vehicle.power_pins)
        ]

        self.pitch = PID(p=1.0, i=0.1, d=0)
        self.roll = PID(p=1.0, i=0.1, d=0)
        self.yaw = PID(p=1.0, i=0.002, d=0)

        logger.info("up")

    def update(self, state):
        state.vehicle.accelerometer = mpu9250.readAccel()
        state.vehicle.gyro = mpu9250.readGyro()
        state.vehicle.magnet = magnetometer.read()
        state.vehicle.deviation = magnetometer.deviation()
        state.vehicle.altitude = altimeter.distance()

        # state.vehicle.temperature = mpu9250.readTemperature()

        self.State.throttle = state.controller.lsy
        self.apply_throttle(self.State.throttle)

        pitch_delta = self.pitch(state.vehicle.accelerometer["x"], state.timer.delta)
        self.apply_pitch(state.vehicle.motors, pitch_delta)

        roll_delta = self.roll(state.vehicle.accelerometer["y"], state.timer.delta)
        self.apply_roll(state.vehicle.motors, roll_delta)

        # yaw_delta = self.yaw(
        #     state.vehicle.deviation["y"],
        #     state.timer.delta
        # )
        # self.apply_yaw(state.vehicle.motors, yaw_delta)

        for motor in state.vehicle.motors:
            motor.tick()

    def apply_throttle(self, throttle):
        for motor in self.State.motors:
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
        for motor in self.State.motors:
            motor.tick()
        GPIO.cleanup()
        logger.info("down")


class Motor(object):
    """
    values below 20 produce what appears to be an alarming beep
    and values above like 90 dont produce much of a change
    so keep a range and adjust the throttle within it
    """

    min_duty_cycle = 30
    max_duty_cycle = 80
    duty_cycle_range = None
    throttle = 0
    dc = 0

    control_pin = None
    power_pin = None

    def __init__(self, control_pin=None, power_pin=None):
        self.duty_cycle_range = self.max_duty_cycle - self.min_duty_cycle

        GPIO.setup(control_pin, GPIO.OUT)
        # 500hz appears to generate the least amount of popping from the motor
        # as long as a prop is installed
        self.control_pin = GPIO.PWM(control_pin, 500)

        self.power_pin = power_pin
        GPIO.setup(self.power_pin, GPIO.OUT)

    def tick(self):
        self.control_pin.start(self.min_duty_cycle)
        duty_cycle = self.min_duty_cycle + (self.throttle * self.duty_cycle_range / 100)
        duty_cycle = max(min(self.max_duty_cycle, duty_cycle), self.min_duty_cycle)

        self.dc = duty_cycle

    def on(self):
        GPIO.output(self.power_pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.power_pin, GPIO.LOW)
