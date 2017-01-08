from collections import namedtuple
import operator

import numpy as np


Frame = namedtuple('Frame', ['time', 'value'])


def lerp(s, e, t):
    return np.add(s, np.multiply(t, np.subtract(e, s)))


class Keyframes(object):
    def __init__(self, frames):
        self.frames = [Frame(time, value) for time, value in frames]

    @property
    def max_time(self):
        return max(map(operator.attrgetter('time'), self.frames))

    def frame_at_time(self, t):
        t = np.clip(t, 0.0, self.max_time)

        if not self.frames:
            raise ValueError('No frames!')

        it = iter(self.frames)
        a = next(it)

        for b in it:
            if a.time <= t < b.time:
                return lerp(a.value, b.value, (t - a.time) / (b.time - a.time))
            a = b

        return a.value
