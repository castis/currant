import time
import logging

import sensors
from utility import PID, GPIO


logger = logging.getLogger('vehicle')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
mpu9250 = sensors.MPU9250()

class Vehicle(object):
    # if i were to implement state management, it would be for this thing
    accel = None
    gyro = None

    def __init__(self, pins):
        if len(pins) != 4:
            raise Exception('incorrect number of motor pins given')

        self.motors = [Motor(pin=pin) for pin in pins]

        # one for each measurement we control
        # self.altitude = PID(p=1, i=0.1, d=0)
        self.pitch = PID(p=1, i=0.1, d=0)
        self.roll = PID(p=1, i=0.1, d=0)
        # self.yaw = PID(p=1, i=0.1, d=0)

        self.accel = mpu9250.readAccel()
        self.gyro = mpu9250.readGyro()

        logger.info('up')

    def tick(self, delta, controller_map):
        self.accel = mpu9250.readAccel()
        self.gyro = mpu9250.readGyro()

        self.apply_throttle((controller_map['RT'] / 255) * 100)

        pitch_delta = self.pitch(self.accel['x'], delta)
        self.apply_pitch(pitch_delta)

        roll_delta = self.roll(self.accel['y'], delta)
        self.apply_roll(roll_delta)

        for motor in self.motors:
            motor.tick()

    def apply_throttle(self, throttle):
        self.motors[0].throttle = throttle
        self.motors[1].throttle = throttle
        self.motors[2].throttle = throttle
        self.motors[3].throttle = throttle

    def apply_pitch(self, delta):
        self.motors[0].throttle -= (delta * 100)
        self.motors[1].throttle -= (delta * 100)
        self.motors[2].throttle += (delta * 100)
        self.motors[3].throttle += (delta * 100)

    def apply_roll(self, delta):
        self.motors[0].throttle -= (delta * 100)
        self.motors[2].throttle -= (delta * 100)
        self.motors[1].throttle += (delta * 100)
        self.motors[3].throttle += (delta * 100)

    def down(self):
        self.apply_throttle(0)
        for motor in self.motors:
            motor.tick()

        GPIO.cleanup()

        logger.info("down")


class Motor(object):
    min_duty_cycle = 30
    max_duty_cycle = 90
    duty_cycle_range = None

    pin = None

    throttle = 0
    dc = 0

    def __init__(self, pin=None):
        # values below 20 produce what appears to be an alarming beep
        # and values above like 90 dont produce much of a change
        # so keep a range and adjust the throttle within it
        self.duty_cycle_range = self.max_duty_cycle - self.min_duty_cycle

        GPIO.setup(pin, GPIO.OUT)

        # 500hz appears to reduce the amount of popping from the motor
        # as long as a prop is installed
        self.pin = GPIO.PWM(pin, 500)
        self.pin.start(self.min_duty_cycle) # duty cycle

    def tick(self):
        duty_cycle = int(self.min_duty_cycle + (self.throttle * self.duty_cycle_range / 100))
        duty_cycle = max(min(self.max_duty_cycle, duty_cycle), self.min_duty_cycle)

        self.dc = duty_cycle
        self.pin.ChangeDutyCycle(duty_cycle)
