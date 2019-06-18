import os
import time
import random
from . logger import *
from . base import Singleton
from . keys import get_input
from . timers import Timer
from . events import EventManager
from . config import config

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
class IdleState(BaseState):
    Name = "idle"

    def tick(self):
        presence = photobooth.presence.check_presence().wait()
        if presence:
            self.states.set_next_state("countdown")
    
@register_state
class CountdownState(BaseState):
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
            photobooth.display.display_text(msg)

@register_state
class CaptureState(BaseState):
    Name = "capture"

    def enter(self, last_state, **kw):
        self.capture_result = photobooth.camera.capture()

    def tick(self):
        if not self.capture_result.poll():
            return
        fn_image = self.capture_result.value
        self.states.set_next_state("process", fn_image=fn_image)

@register_state
class ProcessState(BaseState):
    Name = "process"

    def select_backdrop(self):
        backdrops = photobooth.datastore.backdrops
        keys = list(backdrops.keys())
        bgname = random.choice(keys)
        bgpath = backdrops[bgname]
        return bgpath

    def enter(self, last_state, fn_image=None, **kw):
        self.fn_source = fn_image
        self.fn_backdrop = self.select_backdrop()
        image_name = os.path.split(self.fn_source)[-1]
        self.fn_target = photobooth.datastore.get_path("processed", image_name)
        photolab_request = {
            "fn_source": self.fn_source,
            "fn_target": self.fn_target,
            "steps": [
                "resize",
                "chromakey"
            ],
            "resize": {
                "size": config["images"]["resolution"]
            },
            "chromakey": {
                "fn_backdrop": self.fn_backdrop,
            }
        }
        self.lab_result = photobooth.photolab.process(photolab_request)
        photobooth.display.display_text("processing...")
    
    def tick(self):
        if not self.lab_result.poll():
            return
        _ = self.lab_result.value
        self.states.set_next_state("display", fn_image=self.fn_target)

@register_state
class DisplayState(BaseState):
    Name = "display"
    DelayCount = 10

    def enter(self, last_state, fn_image=None, **kw):
        print("displaying", fn_image)
        photobooth.display.display_image(fn_image)
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.timer.expired:
            self.states.set_next_state("idle")
