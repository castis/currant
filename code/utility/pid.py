import time


class PID(object):

    def __init__(self, p=0, i=0, d=0):
        self.Kp = p
        self.Ki = i
        self.Kd = d

        self._target = 0

        self.previous_feedback = 0
        self.error = None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, v):
        self._target = float(v)

    def __call__(self, feedback, time_delta):
        feedback = float(feedback)

        self.error = self._target - feedback

        alpha = 0

        # proportional
        alpha -= self.Kp * self.error

        # integral
        alpha -= self.Ki * (self.error * time_delta)

        # derivative
        if time_delta > 0:
            alpha -= self.Kd * ((feedback - self.previous_feedback) / float(time_delta))

        self.previous_feedback = feedback

        return alpha
