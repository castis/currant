import time
import logging
import collections
import itertools

import sensors
from utility import PID, GPIO


logger = logging.getLogger("vehicle")


mpu9250 = sensors.MPU9250()
class Magnet:
    initial_read = {"x": 0, "y": 0, "z": 0}
    last_good_read = {"x": 0, "y": 0, "z": 0}

    def __init__(self):
        self.initial_read = self.read()

    def read(self):
        reading = mpu9250.readMagnet()
        if reading:
            self.last_good_read = reading
        return self.last_good_read


hcsr04 = sensors.HCSR04()
class Altimeter(object):
    def read(self):
        # front of sensor is mounted this
        # far from bottom of vehicle
        return hcsr04.distance() - 3.20


altimeter = Altimeter()
magnet = Magnet()

class Vehicle(object):

    class State:
        motor_pins = [19, 16, 26, 20]
        motors = []
        temperature = mpu9250.readTemperature()
        accelerometer = mpu9250.readAccel()
        gyro = mpu9250.readGyro()
        magnet = magnet.read()
        altitude = altimeter.read()
        throttle = 0

    def __init__(self, state):
        state.vehicle =  self.State
        state.vehicle.motors = [Motor(pin=pin) for pin in state.vehicle.motor_pins]

        self.throttle_input = 0

        self.pitch = PID(p=1, i=0.1, d=0)
        self.roll = PID(p=1, i=0.1, d=0)
        self.yaw = PID(p=1, i=0.1, d=0)

        logger.info("up")

    def update(self, state):
        state.vehicle.accelerometer = mpu9250.readAccel()
        state.vehicle.gyro = mpu9250.readGyro()
        state.vehicle.magnet = magnet.read()
        state.vehicle.altitude = altimeter.read()
        state.vehicle.temperature = mpu9250.readTemperature()

        self.State.throttle = max(0, min(state.controller.lsy / 327, 100))
        self.apply_throttle(self.State.throttle)

        pitch_delta = self.pitch(
            state.vehicle.accelerometer['x'],
            state.chronograph.delta
        )
        self.apply_pitch(state.vehicle.motors, pitch_delta)

        roll_delta = self.roll(
            state.vehicle.accelerometer['y'],
            state.chronograph.delta
        )
        self.apply_roll(state.vehicle.motors, roll_delta)

        yaw_delta = self.yaw(
            state.vehicle.accelerometer['y'],
            state.chronograph.delta
        )
        self.apply_roll(state.vehicle.motors, yaw_delta)

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
        motors[0].throttle -= delta * 100
        motors[3].throttle -= delta * 100
        motors[1].throttle += delta * 100
        motors[2].throttle += delta * 100

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
    pin = None
    throttle = 0
    dc = 0

    def __init__(self, pin=None):
        self.duty_cycle_range = self.max_duty_cycle - self.min_duty_cycle
        GPIO.setup(pin, GPIO.OUT)

        # 500hz appears to reduce the amount of popping from the motor
        # as long as a prop is installed
        self.pin = GPIO.PWM(pin, 500)
        self.pin.start(self.min_duty_cycle)

    def tick(self):
        duty_cycle = int(
            self.min_duty_cycle + (self.throttle * self.duty_cycle_range / 100)
        )
        duty_cycle = max(min(self.max_duty_cycle, duty_cycle), self.min_duty_cycle)

        self.dc = duty_cycle
        self.pin.ChangeDutyCycle(duty_cycle)
