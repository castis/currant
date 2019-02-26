import curses
import io
import logging
import os
import psutil
import sys


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
        self.window.addstr(
            0, 0, f"{self.name}:", self.err_color if error else self.name_color
        )
        self.window.addstr(
            1, 0, self.display.format(*args, **kwargs), self.display_color
        )
        self.window.noutrefresh()


class Display(object):
    screen = None

    class State:
        running = False

    def __init__(self, state):
        state.display = self.State
        if not state.args.debug:
            self.up()

    def up(self):
        logger.info("up")
        self.screen = curses.initscr()
        self.State.running = True

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

        self.engine = Cluster(0, 0, (
            "time: {time:.2f}\n"
            "cap: {cap:.1f}\n"
            "fps: {fps:.1f}\n"
            "memory used: {mem:.7f} MiB\n"
        ), name="engine")

        self.controller = Cluster(0, 30, (
            "throttle: {throttle}\n"
            "strafe: {strafe}\n"
            "forward: {forward}\n"
            "spin: {spin}\n"
        ), name="controller")

        row_2 = 6
        self.vehicle = Cluster(row_2, 0, (
            "altitude: {altitude:>6.2f}cm\n"
            "throttle: {throttle:>6.2f}\n"
            "temperature: {temperature:>6.2f}\n"
        ), name="vehicle")

        self.motors = Cluster(row_2, 22, (
            "{0: 2d}  {1: 2d}\n"
            "{2: 2d}  {3: 2d}\n"
        ), name="motors")

        row_3 = 11
        self.accelerometer = Cluster(row_3, 0, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="acc")

        self.gyro = Cluster(row_3, 16, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="gyro")

        self.magnet = Cluster(row_3, 32, (
            "x: {x:>7.3f}\n"
            "y: {y:>7.3f}\n"
            "z: {z:>7.3f}\n"
        ), name="magnet")

        row_4 = 16
        self.log = Cluster(row_4, 0, "{0}", name="log")

        # fmt: on

    def update(self, state):
        if not self.State.running:
            return

        self.screen.erase()
        self.screen.noutrefresh()

        self.engine.update(
            time=state.chronograph.current,
            cap=state.chronograph.cap,
            fps=state.chronograph.fps,
            mem=process.memory_info().rss / float(2 ** 20),
        )

        self.controller.update(
            error=not state.controller.running,
            throttle=state.controller.lsy,
            strafe=state.controller.rsx,
            forward=state.controller.rsy,
            spin=state.controller.lsx,
        )

        self.vehicle.update(
            altitude=state.vehicle.altitude,
            throttle=state.vehicle.throttle,
            temperature=state.vehicle.temperature,
        )

        self.motors.update(
            state.vehicle.motors[0].dc,
            state.vehicle.motors[1].dc,
            state.vehicle.motors[2].dc,
            state.vehicle.motors[3].dc,
        )

        self.accelerometer.update(**state.vehicle.accelerometer)
        self.gyro.update(**state.vehicle.gyro)
        self.magnet.update(**state.vehicle.magnet)

        self.log.update("\n".join(state.log))

        curses.doupdate()

    def down(self):
        if self.State.running:
            curses.echo()
            curses.endwin()
            self.screen = None

        self.State.running = False
        logger.info("down")
