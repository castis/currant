import logging
from time import time, sleep


logger = logging.getLogger("chronograph")


def pluralize(word, n):
    s = "s" if n != 1 else ""
    return f"{n} {word}{s}"


class Chronograph(object):
    class State:
        current = time()
        cap = 20
        fps = 0
        delta = 0

    def __init__(self, state):
        self.started = time()
        logger.info("up")
        state.chronograph = self.State

    def __repr__(self):
        return "%02d:%02d:%02d" % self.since_start()

    def update(self, state):
        duration = 1.0 / self.State.cap - (time() - self.State.current)
        if duration > 0.0:
            sleep(duration)
        self.State.fps = 1.0 / (time() - self.State.current)
        previous = self.State.current
        self.State.current = time()
        self.State.delta = self.State.current - previous

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
