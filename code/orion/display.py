import curses
import io
import logging
import os
import psutil


process = psutil.Process(os.getpid())
logger = logging.getLogger('display')

class Display(object):
    screen = None

    def up(self):
        logger.info('up')
        self.screen = curses.initscr()

        # no cursor
        curses.curs_set(0)

        # turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        # curses.noecho()

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


        self.engine_display = "engine:\n" \
            + " time: {time:.2f}\n" \
            + " fps: {fps:.2f}\n" \
            + " memory used: {mem:.6f} MiB"

        # self.test = curses.newwin(5, 20, 20, 0)
        self.accelerometer_display = "accelerometer:\n" \
            + " x: {x:.3f}\n" \
            + " y: {y:.3f}\n" \
            + " z: {z:.3f}"

        self.gyroscope_display = "gyroscope:\n" \
            + " x: {x:.3f}\n" \
            + " y: {y:.3f}\n" \
            + " z: {z:.3f}"

        self.motor_display = "motors:\n" \
            + " {0: 3d} {1: 3d}\n" \
            + " {2: 3d} {3: 3d}"

        self.controller_display = "controller:\n" \
            + " map: {map}\n" \
            + " raw: {raw}"

    def tick(self, engine):
        if not self.screen:
            return

        self.screen.erase()

        self.screen.addstr(0, 0, self.engine_display.format(**{
            'time': engine.chronograph.current,
            'fps': engine.chronograph.fps,
            'mem': process.memory_info().rss / float(2 ** 20),
        }))

        # test2 = self.accelerometer_display.format(**engine.vehicle.accel)
        # self.down()
        # print(test2)
        # self.test.addstr(0, 10, test2)
        # self.test.refresh()

        # self.screen.addstr(3, 1, "throttle: %s" % (engine.vehicle.outbound_throttle,))
        # self.screen.addstr(4, 1, "pitch: %s" % (engine.vehicle.outbound_pitch,))
        # self.screen.addstr(5, 1, "roll: %s" % (engine.vehicle.outbound_roll,))

        # accel_display = 10
        # self.screen.addstr(accel_display, 0, "accelerometer:")
        # self.screen.addstr(accel_display+1, 1, "x: %s" % (engine.vehicle.state['accel']['x'],))
        # self.screen.addstr(accel_display+2, 1, "y: %s" % (engine.vehicle.state['accel']['y'],))
        # self.screen.addstr(accel_display+3, 1, "z: %s" % (engine.vehicle.state['accel']['z'],))

        # accel_display = 10
        # screen.addstr(accel_display, 0, "accelerometer:")
        # screen.addstr(accel_display+1, 1, "x: %s" % (accel['x'],))
        # screen.addstr(accel_display+2, 1, "y: %s" % (accel['y'],))
        # screen.addstr(accel_display+3, 1, "z: %s" % (accel['z'],))

        self.screen.addstr(5, 0, self.motor_display.format(*[
            engine.vehicle.motors[0].dc, engine.vehicle.motors[1].dc,
            engine.vehicle.motors[2].dc, engine.vehicle.motors[3].dc
        ]))

        # print_these = self.stream.getvalue().split("\n")
        # print_these.reverse()
        # i = 10
        # for line in print_these[:10]:
        #     self.screen.addstr(i, 40, line)
        #     i -= 1

        self.screen.addstr(9, 0, self.controller_display.format(**{
            'map': engine.controller.map,
            'raw': engine.controller.raw,
        }))

        # keep the cursor at the bottom
        self.screen.addstr(curses.LINES-1, 0, "")

        self.screen.refresh()

    def down(self):
        if self.screen:
            curses.echo()
            curses.endwin()
        self.screen = None

        logger.info('down')
