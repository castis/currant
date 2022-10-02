"""
RPi GPIO shim
"""
import logging

logger = logging.getLogger("GPIO")


class Board:
    mode = None
    warnings = True
    channels = {}


class GPIO:
    # constants left to define
    # GPIO.SPI, GPIO.I2C, GPIO.HARD_PWM, GPIO.SERIAL, GPIO.UNKNOWN

    # GPIO modes
    BCM = "BCM"  # BroadCoM numbering
    BOARD = "BOARD"  # board numbering

    # channel modes
    OUT = 0
    IN = 1

    # channel outputs
    LOW = 0
    HIGH = 1

    PUD_DOWN = 0
    PUD_UP = 1

    RISING = 0
    FALLING = 1
    BOTH = 2

    # TODO
    RPI_INFO = "emulated"
    VERSION = None

    @staticmethod
    def setmode(mode):
        Board.mode = mode
        logger.info("GPIO mode: %s" % Board.mode)

    @staticmethod
    def getmode():
        logger.info("GPIO mode requested (%s)" % Board.mode)
        return Board.mode

    @staticmethod
    def setwarnings(switch):
        Board.warnings = switch
        logger.info("set warnings: %s" % ("on" if switch else "off"))

    @staticmethod
    def setup(pin, mode, initial=None, pull_up_down=None):
        Board.channels[pin] = Channel(pin=pin, mode=mode, output=initial)

    @staticmethod
    def PWM(channel, frequency):
        return PWM(channel=channel, frequency=frequency)

    @staticmethod
    def cleanup():
        logger.info("GPIO cleanup")

    @staticmethod
    def wait_for_edge(channel, timeout=1000):
        pass

    @staticmethod
    def add_event_detect(channel, signal=None, callback=None, bouncetime=200):
        pass

    @staticmethod
    def remove_event_detect(channel):
        pass

    @staticmethod
    def event_detected(channel):
        pass

    @staticmethod
    def add_event_callback(channel, callback):
        pass


class Channel:
    def __init__(
        self, pin=None, signal=None, mode=None, output=None, callback=None
    ):
        self.mode = mode
        self.output = output
        self.callback = callback
        self.signal = signal
        logger.info(
            "init channel %s; mode: %s" % (pin, "high" if mode else "low")
        )


class PWM:
    def __init__(self, channel, frequency):
        self.channel = channel
        self.frequency = frequency
        self.duty_cycle = 0
        logger.info(
            "init pwm channel %s; frequency: %s" % (self.channel, frequency)
        )

    def start(self, duty_cycle):
        self.duty_cycle = duty_cycle
        logger.info(
            "start pwm channel %s; duty cycle: %s" % (self.channel, duty_cycle)
        )

    def stop(self):
        logger.info("stop pwm channel %s" % (self.channel))

    def ChangeDutyCycle(self, duty_cycle):
        logger.info(
            "channel %s: duty cycle: from %s to %s"
            % (self.channel, self.duty_cycle, duty_cycle)
        )
        self.duty_cycle = duty_cycle

    def ChangeFrequency(self, frequency):
        logger.info(
            "channel %s: frequency: from %s to %s"
            % (self.channel, self.frequency, frequency)
        )
        self.frequency = frequency
