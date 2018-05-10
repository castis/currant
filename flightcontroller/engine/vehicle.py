import time
import logging
import collections
import itertools

# import sensors
from utility import PID, GPIO


logger = logging.getLogger('vehicle')
# mpu9250 = sensors.MPU9250()


class Throttle(object):
    """
    Maintains the last {window} throttle inputs.
    Averages them to calculate throttle
    """
    window = 10
    last = 0
    value = 0

    def __init__(self):
        self.deque = collections.deque(range(1), self.window)

    def tick(self, throttle_input):
        self.deque.append(throttle_input)
        self.value = sum(i for i in self.deque) / self.window


class Vehicle(object):
    # accel = None
    # gyro = None
    throttle = 0
    # altitude = 0

    def __init__(self, motor_pins=[]):
        if len(motor_pins) != 4:
            raise Exception('incorrect number of motor pins given')

        self.motors = [Motor(pin=pin) for pin in motor_pins]

        # one for each measurement we control
        self.throttle = Throttle()

        # # self.altitude = PID(p=1, i=0.1, d=0)
        # self.pitch = PID(p=1, i=0.1, d=0)
        # self.roll = PID(p=1, i=0.1, d=0)
        # self.yaw = PID(p=1, i=0.1, d=0)

        # # self.hcsr04 = sensors.HCSR04()

        # self.accel = mpu9250.readAccel()
        # self.gyro = mpu9250.readGyro()
        # self.magnet = mpu9250.readMagnet()
        # self.altitude = 0

        logger.info('up')

    def update(self, engine):
        # self.accel = mpu9250.readAccel()
        # self.gyro = mpu9250.readGyro()
        # # self.magnet = mpu9250.readMagnet()
        # # self.altitude = self.hcsr04.altitude

        self.throttle.tick((engine.input.RT / 255) * 100)
        self.apply_throttle(self.throttle.value)

        # pitch_delta = self.pitch(self.accel['x'], delta)
        # self.apply_pitch(pitch_delta)

        # roll_delta = self.roll(self.accel['y'], delta)
        # self.apply_roll(roll_delta)

        # yaw_delta = self.yaw(self.accel['y'], delta)
        # self.apply_roll(yaw_delta)

        for motor in self.motors:
            motor.tick()

    def apply_throttle(self, throttle):
        for motor in self.motors:
            motor.throttle = throttle

    # def apply_pitch(self, delta):
    #     self.motors[0].throttle -= (delta * 100)
    #     self.motors[1].throttle -= (delta * 100)
    #     self.motors[2].throttle += (delta * 100)
    #     self.motors[3].throttle += (delta * 100)

    # def apply_roll(self, delta):
    #     self.motors[0].throttle -= (delta * 100)
    #     self.motors[2].throttle -= (delta * 100)
    #     self.motors[1].throttle += (delta * 100)
    #     self.motors[3].throttle += (delta * 100)

    # def apply_yaw(self, delta):
    #     self.motors[0].throttle -= (delta * 100)
    #     self.motors[3].throttle -= (delta * 100)
    #     self.motors[1].throttle += (delta * 100)
    #     self.motors[2].throttle += (delta * 100)

    def down(self):
        self.apply_throttle(0)
        for motor in self.motors:
            motor.tick()

        # self.hcsr04.down()

        GPIO.cleanup()

        logger.info("down")


class Motor(object):
    """
    values below 20 produce what appears to be an alarming beep
    and values above like 90 dont produce much of a change
    so keep a range and adjust the throttle within it
    """
    min_duty_cycle = 30
    max_duty_cycle = 90
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
        duty_cycle = int(self.min_duty_cycle +
                         (self.throttle * self.duty_cycle_range / 100))
        duty_cycle = max(min(self.max_duty_cycle, duty_cycle),
                         self.min_duty_cycle)

        self.dc = duty_cycle
        self.pin.ChangeDutyCycle(duty_cycle)
