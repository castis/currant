import logging
from time import time
import asyncio


logger = logging.getLogger('chronograph')


def pluralize(word, number):
    plural = 's' if number != 1 else ''
    return f'{number} {word}{plural}'


class Chronograph(object):
    cap = 20
    fps = 0
    current = 0
    previous = 0
    delta = 0
    sleep = 0

    def __init__(self):
        self.started = self.previous = time()
        logger.info('up')

    def __repr__(self):
        return '%02d:%02d:%02d' % self.since_start()

    async def update(self):
        if self.cap > 0:
            self.sleep = 1.0 / self.cap - (time() - self.current)
            if self.sleep > 0.0:
                await asyncio.sleep(self.sleep)
        self.fps = 1.0 / (time() - self.current)
        self.previous = self.current
        self.current = time()
        self.delta = self.current - self.previous

    def since_start(self):
        seconds = int(time() - self.started)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return (h, m, s)

    def get_run_time(self):
        (h, m, s) = self.since_start()
        run_time = []

        if h > 0:
            run_time.append(pluralize('hour', h))
        if m > 0:
            run_time.append(pluralize('minute', m))
        run_time.append(pluralize('second', s))

        run_time_len = len(run_time)
        if run_time_len == 3:
            run_time = f'{run_time[0]}, {run_time[1]}, and {run_time[2]}'
        elif run_time_len == 2:
            run_time = f'{run_time[0]} and {run_time[1]}'
        else:
            run_time = run_time[0]

        return run_time

    def down(self):
        logger.info('down')
        logger.info(f'run time: {self.get_run_time()}')
