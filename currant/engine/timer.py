import logging
from time import sleep, time

logger = logging.getLogger("timer")


def pluralize(word: str, n: int) -> str:
    s = "s" if n != 1 else ""
    return f"{n} {word}{s}"


def segmented(started: int) -> tuple[int, int, int]:
    seconds = int(time() - started)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m, s


def get_run_time(started):
    run_time = []
    (h, m, s) = segmented(started)
    if h > 0:
        run_time.append(pluralize("hour", h))
    if m > 0:
        run_time.append(pluralize("minute", m))
    run_time.append(pluralize("second", s))
    return ", ".join(run_time)


class Timer(object):
    class State:
        current = time()
        cap = 20
        fps = 0
        frames = 0
        delta = 0
        highest_delta = 0

    def __init__(self, state):
        self.started = time()
        logger.info("up")
        state.timer = self.State

    def update(self, state):
        duration = 1.0 / self.State.cap - (time() - self.State.current)
        if duration > 0.0:
            sleep(duration)
        self.State.fps = 1.0 / (time() - self.State.current)
        previous = self.State.current
        self.State.current = time()
        self.State.delta = self.State.current - previous
        if self.State.delta > self.State.highest_delta:
            self.State.highest_delta = self.State.delta
        self.State.frames = self.State.frames + 1

    def down(self):
        logger.info("down")
        logger.info(f"run time: {get_run_time(self.started)}")
