import logging
from time import time, sleep


logger = logging.getLogger('chronograph')

def pluralize_time(word, number):
    return "%s %s%s" % (number, word, 's' if number != 1 else '')

class Chronograph(object):

    def __init__(self):
        self.started = time()
        self.current = time()
        self.previous = 0
        self.delta = 0
        self.fps = 0
        self.cap = 60
        # self.cap = 0

        logger.info('up')

    def pre_loop(self):
        self.current = time()
        self.delta = self.current - self.previous

    def post_loop(self):
        if self.cap > 0:
            sleep_for = 1.0 / self.cap - (time() - self.current)
            if sleep_for > 0.0:
                sleep(sleep_for)
        self.fps = 1 / (time() - self.current)
        self.previous = self.current

    def down(self):
        seconds = int(time() - self.started)
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

        logger.info('down')
        logger.info('run time: %s' % run_time)
