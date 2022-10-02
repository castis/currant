import time


class PID(object):
    def __init__(self, p=0, i=0, d=0):
        self.Kp = p
        self.Ki = i
        self.Kd = d

        self._target = 0

        self.previous_feedback = 0
        self.error = None

    def __unicode__(self):
        return "PID controller"

    def __format__(self, data):
        return self.__unicode__()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, v):
        self._target = float(v)

    def __call__(self, feedback, time_delta):
        _feedback = float(feedback)

        self.error = self._target - _feedback

        alpha = 0

        # proportional
        alpha -= self.Kp * self.error

        # integral
        alpha -= self.Ki * (self.error * time_delta)

        # derivative
        if time_delta > 0:
            alpha -= self.Kd * (
                (_feedback - self.previous_feedback) / float(time_delta)
            )

        self.previous_feedback = _feedback

        return alpha
