import time
import logging

from utility import PID
from sensors import MPU9250

mpu9250 = MPU9250()

logger = logging.getLogger('vehicle')

try:
    import RPi.GPIO as GPIO
except ImportError:
    logger.error("loading stub GPIO library")
    from utility import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Vehicle():
    outbound_throttle = 0
    outbound_pitch = 0
    outbound_roll = 0

    def __init__(self, motor_pins):
        logger.info('hi')

        if len(motor_pins) != 4:
            raise Exception('incorrect number of motor pins given')

        self.motors = [Motor(pin=pin) for pin in motor_pins]

        # one for each measurement we control
        self.throttle = PID(p=1, i=0.1, d=0)
        # self.altitude = PID(p=1, i=0.1, d=0)
        self.pitch = PID(p=1, i=0.1, d=0)
        self.roll = PID(p=1, i=0.1, d=0)
        # self.yaw = PID(p=1, i=0.1, d=0)

        logger.info('ready')

    def tick(self, dt, controller_map):
        accel = mpu9250.readAccel()
        # gyro = mpu9250.readGyro()

        self.outbound_throttle = (controller_map['RT'] / 255) * 100
        self.outbound_throttle = self.throttle(feedback=self.outbound_throttle, dt=dt)
        self.apply_throttle(self.outbound_throttle)

        self.outbound_pitch = self.pitch(feedback=accel['x'], dt=dt)
        self.apply_pitch(self.outbound_pitch)

        self.outbound_roll = self.roll(feedback=accel['y'], dt=dt)
        self.apply_roll(self.outbound_roll)

        self.render()

    def apply_throttle(self, throttle_response):
        self.motors[0].throttle = throttle_response
        self.motors[1].throttle = throttle_response
        self.motors[2].throttle = throttle_response
        self.motors[3].throttle = throttle_response

    def apply_pitch(self, pitch_adjustment):
        self.motors[0].throttle -= (pitch_adjustment * 100)
        self.motors[1].throttle -= (pitch_adjustment * 100)
        self.motors[2].throttle += (pitch_adjustment * 100)
        self.motors[3].throttle += (pitch_adjustment * 100)

    def apply_roll(self, roll_adjustment):
        self.motors[0].throttle -= (roll_adjustment * 100)
        self.motors[2].throttle -= (roll_adjustment * 100)
        self.motors[1].throttle += (roll_adjustment * 100)
        self.motors[3].throttle += (roll_adjustment * 100)

    def render(self):
        for motor in self.motors:
            motor.render()

    def shutdown(self, signum=None, frame=None):
        logger.info("shutdown")

        self.apply_throttle(0)
        self.render()

        GPIO.cleanup()

        logger.info("halted")


class Motor():
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

    def render(self):
        duty_cycle = int(self.min_duty_cycle + (self.throttle * self.duty_cycle_range / 100))
        duty_cycle = max(min(self.max_duty_cycle, duty_cycle), self.min_duty_cycle)

        self.dc = duty_cycle
        self.pin.ChangeDutyCycle(duty_cycle)
