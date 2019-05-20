import time
from . logger import *
from . base import Singleton
from . keys import get_input
from . timer import Timer

"""
import cProfile as profile
import atexit
profiler = profile.Profile()
#profiler.enable()
def save_profiler():
    profiler.dump_stats("photobooth.prof")
atexit.register(save_profiler)
"""

def register_state(cls):
    machine = StateMachine()
    machine.add_state(cls)
    return cls

class BaseState(object):
    Name = "BaseState"

    def enter(self, last_state):
        pass

    def tick(self):
        pass

    def enter(self, last_state):
        pass

    def exit(self, next_state):
        pass

    def __str__(self):
        return self.Name

    def __eq__(self, other):
        if isinstance(other, State):
            return self.Name == other.Name
        if type(other) == str:
            return self.Name == other
        raise TypeError("State can not compare to '%s'" % type(other))

class StateMachine(Singleton):
    States = {}

    def __new__(cls):
        instance = super().__new__(cls)
        if not hasattr(instance, "current_state"):
            instance.current_state = None
        if not hasattr(instance, "states"):
            instance.states = {}
        return instance

    def add_state(self, state_class):
        state = state_class()
        self.states[state.Name] = state

    def enter(self, state_name):
        logmsg = "Entering state '%s'" % state_name
        next_state = self.states[state_name]
        if self.current_state is not None:
            logmsg += " from state '%s'" % self.current_state
            self.current_state.exit(next_state)
        info(logmsg)
        next_state.enter(self.current_state)
        self.current_state = next_state

    def tick(self):
        next_state_name = self.current_state.tick()
        if next_state_name is not None:
            self.enter(next_state_name)
        return self.current_state.Name

@register_state
class IdleBaseState(BaseState):
    Name = "idle"

    def tick(self):
        inch = get_input()
        if inch:
            return "countdown"
    
@register_state
class CountdownBaseState(BaseState):
    Name = "countdown"
    DelayCount = 3

    def enter(self, last_state):
        self.timer = Timer(self.DelayCount)
        self.count = self.DelayCount
        self.last_report = None

    def tick(self):
        if self.timer.expired:
            return "capture"
        elapsed = int(self.timer.elapsed)
        if elapsed != self.last_report:
            self.last_report = elapsed
            msg = str(self.DelayCount - elapsed)
            print(msg, self.timer.elapsed)
            photobooth.display.show_text(msg)
            #profiler.runcall(photobooth.display.show_text, msg)
            #print(self.timer.elapsed)

@register_state
class CaptureBaseState(BaseState):
    Name = "capture"

    def enter(self, last_state):
        pass

    def tick(self):
        return "process"

@register_state
class ProcessBaseState(BaseState):
    Name = "process"

    def enter(self, last_state):
        pass

    def tick(self):
        return "display"

@register_state
class DisplayBaseState(BaseState):
    Name = "display"
    DelayCount = 10

    def enter(self, last_state):
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.timer.expired:
            return "idle"
