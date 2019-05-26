import time
from . logger import *
from . base import Singleton
from . keys import get_input
from . timers import Timer
from . events import EventManager

def register_state(cls):
    machine = StateMachine()
    machine.add_state(cls)
    return cls

class BaseState(object):
    Name = "BaseState"

    def __init__(self):
        self.events = EventManager()
        self.states = StateMachine()

    def enter(self, last_state, **kw):
        pass

    def tick(self):
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

    def init_instance(self):
        self._current_state = None
        self._next_state = None
        self.states = {}

    def add_state(self, state_class):
        state = state_class()
        self.states[state.Name] = state

    def set_next_state(self, name, **kw):
        assert self._next_state is None
        assert name in self.states
        self._next_state = (name, kw)

    def switch(self):
        assert self._next_state is not None
        (next_state_name, next_kw) = self._next_state
        logmsg = "Entering state '%s'" % next_state_name
        next_state = self.states[next_state_name]
        if self._current_state is not None:
            logmsg += " from state '%s'" % self._current_state
            self._current_state.exit(next_state)
        info(logmsg)
        next_state.enter(self._current_state, **next_kw)
        self._next_state = None
        self._current_state = next_state

    def tick(self):
        if self._next_state is not None:
            self.switch()
        if self._current_state:
            self._current_state.tick()

@register_state
class IdleBaseState(BaseState):
    Name = "idle"

    def tick(self):
        inch = get_input()
        if inch:
            self.states.set_next_state("countdown")
    
@register_state
class CountdownBaseState(BaseState):
    Name = "countdown"
    DelayCount = 3

    def enter(self, last_state, **kw):
        self.timer = Timer(self.DelayCount)
        self.count = self.DelayCount
        self.last_report = None

    def tick(self):
        if self.timer.expired:
            self.states.set_next_state("capture")
            return
        elapsed = int(self.timer.elapsed)
        if elapsed != self.last_report:
            self.last_report = elapsed
            msg = str(self.DelayCount - elapsed)
            #print(msg, self.timer.elapsed)
            photobooth.display.show_text(msg)

@register_state
class CaptureBaseState(BaseState):
    Name = "capture"

    def capture_handler(self, event):
        self.states.set_next_state("process", image_filename=event.data["image_filename"])
        self.events.remove_handler("capture", self.capture_handler)

    def enter(self, last_state, **kw):
        self.events.add_handler("capture", self.capture_handler)
        img = photobooth.camera.capture()

@register_state
class ProcessBaseState(BaseState):
    Name = "process"

    def enter(self, last_state, image_filename=None, **kw):
        self.image_filename=image_filename
    
    def tick(self):
        self.states.set_next_state("display", image_filename=self.image_filename)

@register_state
class DisplayBaseState(BaseState):
    Name = "display"
    DelayCount = 10

    def enter(self, last_state, image_filename=None, **kw):
        img_path = photobooth.datastore.get_path("negatives", image_filename)
        photobooth.display.show_image(img_path)
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.timer.expired:
            self.states.set_next_state("idle")
