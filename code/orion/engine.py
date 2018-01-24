import logging
import traceback

from time import time, sleep

from .controller import Controller
from .display import Display
from .vehicle import Vehicle, Motor


logger = logging.getLogger('engine')
logger.setLevel(logging.DEBUG)


class Engine():
    running = False
    display = None

    vehicle = None
    controller = None

    def __init__(self, args, **kwargs):
        self.headless = args.headless

        self.started = time()

        # timekeeping
        self.current = 0
        self.time_previous = 0
        self.time_current = 0
        self.time_delta = 0
        self.fps = 0
        self.fps_cap = kwargs.get('fps_cap', 60)

        logger.info('start')

        try:
            self.vehicle = Vehicle(motor_pins=[27, 7, 21, 13])
            self.controller = Controller()

            logger.info('here we go')

            if not self.headless:
                # dramatic pause so we can see the log
                sleep(1)
                self.display = Display()
                self.display.on()
        except Exception as e:
            tb = traceback.format_exc()
            logger.info('exception caught\n%s' % tb)
            self.shutdown()
            return

        self.run()

    def run(self):
        self.running = True
        try:
            while self.running:
                # time management
                self.time_current = time()
                self.time_delta = self.time_current - self.time_previous

                self.vehicle.tick(self.time_delta, self.controller.map)

                if self.display:
                    self.display.update(self)

                # end-of-loop management
                if self.fps_cap > 0:
                    sleep_for = 1.0 / self.fps_cap - (time() - self.time_current)
                    if sleep_for > 0.0:
                        sleep(sleep_for)
                self.fps = round(1 / (time() - self.time_current))
                self.time_previous = self.time_current

        except KeyboardInterrupt:
            if self.display:
                self.display.off()
            logger.info('caught ^C')

        except Exception as e:
            if self.display:
                self.display.off()
            tb = traceback.format_exc()
            logger.info('exception caught\n%s' % tb)

        finally:
            self.shutdown()

    def shutdown(self):
        logger.info('shutdown')

        if self.vehicle:
            self.vehicle.shutdown()

        if self.controller:
            self.controller.shutdown()

        logger.info('run time: %s' % self.run_time())

    def run_time(self):
        seconds = int(time() - self.started,)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        run_time = []

        if h > 0:
            run_time.append(pluralize_time('hour', h))
        if m > 0:
            run_time.append(pluralize_time('minute', m))
        run_time.append(pluralize_time('second', s))

        run_time_len = len(run_time)
        if run_time_len == 3:
            run_time = "%s, %s, and %s" % (run_time[0], run_time[1], run_time[2])
        elif run_time_len == 2:
            run_time = "%s and %s" % (run_time[0], run_time[1])
        else:
            run_time = run_time[0]

        return run_time

def pluralize_time(word, number):
    return "%s %s%s" % (number, word, 's' if number != 1 else '')
