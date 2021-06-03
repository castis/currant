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


def get_run_time(started: int) -> str:
    run_time = []
    (h, m, s) = segmented(started)
    if h > 0:
        run_time.append(pluralize("hour", h))
    if m > 0:
        run_time.append(pluralize("minute", m))
    run_time.append(pluralize("second", s))
    return ", ".join(run_time)


class Timer(object):
    current = time()
    cap = 30
    fps = 0
    frames = 0
    delta = 0
    highest_delta = 0

    def __init__(self, args):
        self.started = time()
        logger.info("up")

    def update(self):
        duration = 1.0 / self.cap - (time() - self.current)
        if duration > 0.0:
            sleep(duration)
        self.fps = 1.0 / (time() - self.current)
        previous = self.current
        self.current = time()
        self.delta = self.current - previous
        if self.delta > self.highest_delta:
            self.highest_delta = self.delta
        self.frames = self.frames + 1

    def down(self):
        logger.info("down")
        logger.info(f"run time: {get_run_time(self.started)}")
