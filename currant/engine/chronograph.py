import logging
from time import time
import asyncio


logger = logging.getLogger("chronograph")


def pluralize(word, n):
    s = "s" if n != 1 else ""
    return f"{n} {word}{s}"


class Chronograph(object):
    cap = 1
    fps = 0
    current = 0
    previous = 0
    delta = 0
    sleep = 0

    def __init__(self):
        self.started = self.previous = time()
        logger.info("up")

    def __repr__(self):
        return "%02d:%02d:%02d" % self.since_start()

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
        run_time = []
        (h, m, s) = self.since_start()
        if h > 0:
            run_time.append(pluralize("hour", h))
        if m > 0:
            run_time.append(pluralize("minute", m))
        run_time.append(pluralize("second", s))
        return ", ".join(run_time)

    def down(self):
        logger.info("down")
        logger.info(f"run time: {self.get_run_time()}")
