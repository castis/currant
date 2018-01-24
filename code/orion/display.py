import curses
import logging
import io


logger = logging.getLogger('display')


class Display():
    screen = None

    def on(self):
        logger.info('on')
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

        self.engine_display = curses.newwin(3, 40, 0, 0)

    def update(self, engine):
        if not self.screen:
            return

        self.screen.erase()

        self.screen.addstr(0, 0, "engine:")
        self.screen.addstr(1, 1, "time: %s" % engine.time_current)
        self.screen.addstr(2, 1, "fps: %s" % engine.fps)

        self.screen.addstr(3, 1, "throttle: %s" % (engine.vehicle.outbound_throttle,))
        self.screen.addstr(4, 1, "pitch: %s" % (engine.vehicle.outbound_pitch,))
        self.screen.addstr(5, 1, "roll: %s" % (engine.vehicle.outbound_roll,))

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

        motor_display = 7
        self.screen.addstr(motor_display, 0, "motors:")
        self.screen.addstr(motor_display+1, 1, "%s" % engine.vehicle.motors[0].dc)
        self.screen.addstr(motor_display+1, 7, "%s" % engine.vehicle.motors[1].dc)
        self.screen.addstr(motor_display+2, 1, "%s" % engine.vehicle.motors[2].dc)
        self.screen.addstr(motor_display+2, 7, "%s" % engine.vehicle.motors[3].dc)

        # print_these = self.stream.getvalue().split("\n")
        # print_these.reverse()
        # i = 10
        # for line in print_these[:10]:
        #     self.screen.addstr(i, 40, line)
        #     i -= 1

        self.screen.addstr(curses.LINES - 5, 0, "controller: %s" % (engine.controller,))
        self.screen.addstr(curses.LINES - 4, 0, " map: %s" % (engine.controller.map,))
        self.screen.addstr(curses.LINES - 3, 0, " raw: %s" % (engine.controller.raw,))

        self.screen.addstr(curses.LINES-1, 0, "") # keep the cursor at the bottom

        self.screen.refresh()


    def off(self):
        if self.screen:
            del self.screen

        curses.echo()
        curses.endwin()

        logger.info('off')
