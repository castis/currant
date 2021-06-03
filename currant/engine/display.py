import curses
import io
import logging
import os
import sys

import psutil

process = psutil.Process(os.getpid())
logger = logging.getLogger("display")


class Cluster:
    def __init__(self, x, y, display, name):
        self.window = curses.newwin(0, 0, x, y)
        self.name = name
        self.name_color = curses.color_pair(1)
        self.err_color = curses.color_pair(3)
        self.display = display
        self.display_color = curses.color_pair(2)

    def update(self, *args, error=False, **kwargs):
        self.window.addstr(0, 0, f"{self.name}:", self.err_color if error else self.name_color)
        logger.info(self.display.format(*args, **kwargs))
        logger.info(self.display_color)
        self.window.addstr(1, 0, self.display.format(*args, **kwargs), self.display_color)
        self.window.noutrefresh()


class Display(object):
    screen = None
    prev_stdout = None

    running = False

    def __init__(self, args, timer, controller, vehicle):
        self.timer = timer
        self.controller = controller
        self.vehicle = vehicle
        self.enabled = args.display_enabled

        self.up()

    def up(self):
        if not self.enabled:
            logger.info("display not enabled")
            return

        logger.info("up")
        self.screen = curses.initscr()
        self.running = True

        # if anything manages to get printed it messes with curses
        self.prev_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

        # no cursor
        curses.curs_set(0)

        # turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()

        # in keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        self.screen.keypad(1)
        self.screen.nodelay(1)

        # harmless if the terminal doesn't have color;
        # user can test with has_color() later on. the try/catch
        # works around a minor bit of over-conscientiousness in the curses
        # module -- the error return from C start_color() is ignorable.
        try:
            curses.start_color()
        except:
            pass

        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        # fmt: off

        self.engineCluster = Cluster(0, 0, (
            "time: {time:.2f}\n"
            "frame number: {frame}\n"
            "fps: {fps:.2f}/{cap:.0f}\n"
            "highest d: {highest_delta:.2f}\n"
            "memory used: {mem} MiB\n"
        ), name="engine")

        self.controllerCluster = Cluster(0, 30, (
            "throttle: {throttle}\n"
            "strafe: {strafe}\n"
            "forward: {forward}\n"
            "spin: {spin}\n"
        ), name="controller")

        row_2 = 7
        self.vehicleCluster = Cluster(row_2, 0, (
            "altitude: {altitude:>6.2f}cm\n"
            "throttle: {throttle:>6.2f}\n"
            "temperature: {temperature:>6.2f}\n"
        ), name="vehicle")

        self.motorCluster = Cluster(row_2, 22, (
            "{0:>3.3f}  {1:>3.3f}\n"
            "{2:>3.3f}  {3:>3.3f}\n"
        ), name="motors")

        row_3 = 12
        self.accelerometer = Cluster(row_3, 0, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="accel")

        self.gyro = Cluster(row_3, 15, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="gyro")

        self.magnet = Cluster(row_3, 30, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="magnet")

        self.deviation = Cluster(row_3, 45, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="deviation")

        row_4 = 17
        self.log = Cluster(row_4, 0, "{0}", name="log")

        # fmt: on

    def update(self):
        if not self.running:
            return

        self.screen.erase()
        self.screen.noutrefresh()

        self.engineCluster.update(
            time=self.timer.current,
            cap=self.timer.cap,
            fps=self.timer.fps,
            frame=self.timer.frames,
            highest_delta=self.timer.highest_delta,
            mem=process.memory_info().rss / float(2 ** 20),
        )

        self.controllerCluster.update(
            error=not self.controller.running,
            throttle=self.controller.buttons.lsy,
            strafe=self.controller.buttons.rsx,
            forward=self.controller.buttons.rsy,
            spin=self.controller.buttons.lsx,
        )

        self.vehicleCluster.update(
            altitude=self.vehicle.altitude,
            throttle=self.vehicle.throttle,
            temperature=self.vehicle.temperature,
        )

        self.motorCluster.update(
            self.vehicle.motors[0].dc,
            self.vehicle.motors[1].dc,
            self.vehicle.motors[2].dc,
            self.vehicle.motors[3].dc,
        )

        self.accelerometer.update(**self.vehicle.accelerometer)
        self.gyro.update(**self.vehicle.gyro)
        self.magnet.update(**self.vehicle.magnet)
        self.deviation.update(**self.vehicle.deviation)

        # self.log.update("\n".join(state.log))

        curses.doupdate()

    def down(self):
        if self.screen:
            curses.echo()
            curses.endwin()
            self.screen = None

        # reinstate stdout
        if self.prev_stdout:
            sys.stdout = self.prev_stdout

        self.running = False
        logger.info("down")
