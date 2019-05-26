import time
import enum
from . base import Singleton

class Timer(object):
    def __init__(self, length=None):
        self.reset()
        self.length = length

    def reset(self):
        self.timestamp = time.time()

    @property
    def elapsed(self):
        return time.time() - self.timestamp

    @property
    def expired(self):
        if self.length is None:
            return False
        return self.elapsed >= self.length
    
    def wait(self):
        delta = max(0, self.length - self.elapsed)
        if not delta:
            return
        time.sleep(delta)

class TimerModes(enum.Enum):
    TIMEOUT = enum.auto()
    INTERVAL = enum.auto()

class Timers(Singleton):
    def init_instance(self):
        self._next_timer_id = 0
        self.timers = {}

    def new_timer_id(self):
        self._next_timer_id += 1
        return self._next_timer_id

    def set_timeout(self, length=None, callback=None):
        timer_id = self.new_timer_id()
        timer = Timer(length)
        self.timers[timer_id] = (timer, callback, TimerModes.TIMEOUT)
        return timer_id

    def set_interval(self, length=None, callback=None):
        timer_id = self.new_timer_id()
        timer = Timer(length)
        self.timers[timer_id] = (timer, callback, TimerModes.INTERVAL)
        return timer_id
    
    def cancel(self, timer_id):
        if timer_id not in self.timers:
            raise KeyError("timer does not exist")
        del self.timers[timer_id]

    def tick(self):
        timers = self.timers.copy()
        for (timer_id, info) in timers.items():
            (timer, callback, mode) = info
            if timer.expired:
                callback()
                if mode == TimerModes.INTERVAL:
                    timer.reset()
                else:
                    del self.timers[timer_id]

