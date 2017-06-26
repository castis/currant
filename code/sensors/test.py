import sys

# https://docs.python.org/3/howto/curses.html
import curses
import time
from sensors import MPU9250

mpu9250 = MPU9250()


def main(screen):

    # accelMagneto = sensors.AccelMagneto()
    height, width = screen.getmaxyx()

    while True:
        accel = mpu9250.readAccel()
        screen.addstr(1, 2, "Accelerometer:")
        screen.addstr(2, 3, "X: %s" % accel['x'])
        screen.addstr(3, 3, "Y: %s" % accel['y'])
        screen.addstr(4, 3, "Z: %s" % accel['z'])

        # magnet = mpu9250.readMagnet()
        # screen.addstr(6, 2, "Magnetometer:")
        # screen.addstr(7, 3, "X: %s" % magnet['x'])
        # screen.addstr(8, 3, "Y: %s" % magnet['y'])
        # screen.addstr(9, 3, "Z: %s" % magnet['z'])

        gyro = mpu9250.readGyro()
        screen.addstr(6, 2, "Gyroscope:")
        screen.addstr(7, 3, "X: %s" % gyro['x'])
        screen.addstr(8, 3, "Y: %s" % gyro['y'])
        screen.addstr(9, 3, "Z: %s" % gyro['z'])

        # screen.addstr(height-1, width-1, "x")
        time.sleep(0.1)
        screen.refresh()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print('caught ctrl-C')
    finally:
        curses.echo()
        curses.nocbreak()
        curses.endwin()
