import os
import time
import random
from . logger import *
from . base import Singleton
from . keys import get_input
from . timers import Timer
from . events import EventManager
from . config import config
from . session import Session

def register_state(cls):
    machine = StateMachine()
    machine.add_state(cls)
    return cls

class BaseState(object):
    Name = "BaseState"
    Timeout = 30

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
    InitialState = "idle"
    States = {}

    def init_instance(self):
        self._current_state = None
        self._next_state = None
        self._timeout_timer = None
        self.global_state = {}
        self.session = None
        self.states = {}

    def set_global(self, key, value):
        self.global_state[key] = value

    def get_global(self, key):
        return self.global_state.get(key, None)

    def pop_global(self, key):
        return self.global_state.pop(key, None)

    def new_session(self):
        self.session = Session()

    def close_session(self):
        if self.session is None:
            return
        self.session.close()

    def add_state(self, state_class):
        state = state_class()
        self.states[state.Name] = state

    def set_next_state(self, state_name=None, **kw):
        assert self._next_state is None
        if state_name not in self.states:
            msg = "unknown state '%s'" % state_name
            raise KeyError(msg)
        self._next_state = (state_name, kw)

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
        if next_state.Timeout != -1:
            self._timeout_timer = Timer(next_state.Timeout)
        self._next_state = None
        self._current_state = next_state

    def tick(self):
        if self._timeout_timer != None:
            if self._timeout_timer.expired:
                self._timeout_timer = None
                msg = "Timeout occured within '%s' state, going back to '%s'" % (self._current_state.Name, self.InitialState)
                error(msg)
                self._current_state = None
                self.set_next_state(self.InitialState)
        if self._next_state is not None:
            self._timeout_timer = None
            self.switch()
        if self._current_state:
            self._current_state.tick()

@register_state
class IdleState(BaseState):
    Name = "idle"
    Timeout = -1

    def enter(self, last_state, **kw):
        self._long_idle = False
        self._long_idle_timer = Timer(config["powersave"]["timeout"])

    def tick(self):
        presence = photobooth.presence.check_presence().wait()
        if presence:
            next_state = {"state_name": "ask_backdrop"}
            self.states.new_session()
            self.states.set_next_state("speak", topic="introduction", next_state=next_state)
        if not self._long_idle:
            if self._long_idle_timer.expired:
                self.lights.off()
                self.projector.off()

    def exit(self, next_state):
        if self._long_idle:
            self.lights.on()
            self.projector.on()

@register_state
class Speak(BaseState):
    Name = "speak"

    def enter(self, last_state, topic=None, next_state=None, wait=True, **kw):
        self.next_state = next_state
        self.wait = wait
        self.speaker = photobooth.audio.speak_dialog(topic)

    def tick(self):
        if self.wait and not self.speaker.poll():
            return
        self.states.set_next_state(**self.next_state)
    
@register_state
class AskBackdrop(BaseState):
    Name = "ask_backdrop"
    DelayCount = 20

    def enter(self, last_state):
        self.speaker = photobooth.audio.speak_dialog("question_pick")
        self.speaker.wait()
        self.listen = photobooth.stt.listen()
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.listen.poll():
            word = self.listen.value
            if word == "yes":
                self.states.set_next_state("pick_backdrop")
            elif word == "no":
                self.speaker = photobooth.audio.speak_dialog("random_pick")
                self.speaker.wait()
                self.states.set_next_state("ready")
            elif word:
                self.speaker = photobooth.audio.speak_dialog("no_understand")
                self.speaker.wait()
                self.listen = photobooth.stt.listen()
            else:
                self.listen = photobooth.stt.listen()
        elif self.timer.expired:
            photobooth.stt.stop()
            self.speaker = photobooth.audio.speak_dialog("random_pick")
            self.speaker.wait()
            self.states.set_next_state("ready")
    
@register_state
class PickBackdrop(BaseState):
    Name = "pick_backdrop"
    DelayCount = 20

    def enter(self, last_state):
        self.backdrops = list(photobooth.datastore.backdrops.keys())
        random.shuffle(self.backdrops)
        self.pop_and_show()

    def pop_and_show(self):
        self.selected_backdrop = self.backdrops.pop()
        bgpath = photobooth.datastore.backdrops[self.selected_backdrop]
        photobooth.display.display_image(bgpath)
        self.speaker = photobooth.audio.speak_dialog("question_backdrop")
        self.speaker.wait()
        self.listen = photobooth.stt.listen()
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.listen.poll():
            word = self.listen.value
            if word == "yes":
                self.states.set_global("backdrop", self.selected_backdrop)
                self.states.set_next_state("ready")
            elif word == "no":
                self.pop_and_show()
            elif word:
                self.speaker = photobooth.audio.speak_dialog("no_understand")
                self.speaker.wait()
                self.listen = photobooth.stt.listen()
            else:
                self.listen = photobooth.stt.listen()
        elif self.timer.expired:
            self.pop_and_show()

@register_state
class SameBackdrop(BaseState):
    Name = "same_backdrop"
    DelayCount = 20

    def enter(self, last_state):
        self.speaker = photobooth.audio.speak_dialog("same_backdrop")
        self.speaker.wait()
        self.listen = photobooth.stt.listen()
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.listen.poll():
            word = self.listen.value
            if word == "yes":
                bgname = self.states.pop_global("last_backdrop")
                self.states.set_global("backdrop", bgname)
                self.states.set_next_state("ready")
            elif word == "no":
                self.states.set_next_state("ask_backdrop")
            elif word:
                self.speaker = photobooth.audio.speak_dialog("no_understand")
                self.speaker.wait()
                self.listen = photobooth.stt.listen()
            else:
                self.listen = photobooth.stt.listen()
        elif self.timer.expired:
            photobooth.stt.stop()
            self.speaker = photobooth.audio.speak_dialog("random_pick")
            self.speaker.wait()
            self.states.set_next_state("ready")


@register_state
class Ready(BaseState):
    Name = "ready"
    DelayCount = 20

    def enter(self, last_state):
        self.speaker = photobooth.audio.speak_dialog("ready")
        self.speaker.wait()
        self.listen = photobooth.stt.listen()
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.listen.poll():
            word = self.listen.value
            if word == "ready":
                self.states.set_next_state("countdown")
            elif word:
                self.speaker = photobooth.audio.speak_dialog("no_understand")
                self.speaker.wait()
                self.listen = photobooth.stt.listen()
            else:
                self.listen = photobooth.stt.listen()
        elif self.timer.expired:
            photobooth.stt.stop()
            self.speaker = photobooth.audio.speak_dialog("bored")
            self.speaker.wait()
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
            photobooth.audio.speak(msg)
            photobooth.display.display_text(msg)

@register_state
class CaptureState(BaseState):
    Name = "capture"
    Timeout = 10

    def enter(self, last_state, **kw):
        self.states.session.inc_image()
        fn_target = self.states.session.capture_path
        self.capture_result = photobooth.camera.capture(fn_target=fn_target)

    def tick(self):
        if not self.capture_result.poll():
            return
        fn_image = self.capture_result.value
        next_state = {"state_name": "process", "fn_image": fn_image}
        self.states.set_next_state("speak", topic="processing", next_state=next_state, wait=False)

@register_state
class ProcessState(BaseState):
    Name = "process"
    Timeout = 60

    def select_backdrop(self):
        backdrops = photobooth.datastore.backdrops
        bgname = self.states.pop_global("backdrop")
        if bgname == None:
            keys = list(backdrops.keys())
            bgname = random.choice(keys)
        bgpath = backdrops[bgname]
        self.states.set_global("last_backdrop", bgname)
        return bgpath

    def enter(self, last_state, fn_image=None, **kw):
        self.fn_source = fn_image
        self.fn_backdrop = self.select_backdrop()
        image_name = os.path.split(self.fn_source)[-1]
        self.fn_target = self.states.session.processed_path
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
    Timeout = 15

    def enter(self, last_state, fn_image=None, **kw):
        photobooth.display.display_image(fn_image)
        self.speaker = photobooth.audio.speak_dialog("appraisal")
        self.timer = Timer(self.DelayCount)

    def exit(self, next_state):
        speaker = photobooth.audio.speak_dialog("tips")
        speaker.wait()

    def tick(self):
        if not self.timer.expired:
            return
        presence = photobooth.presence.check_presence().wait()
        if presence:
            next_state = "same_backdrop"
        else:
            next_state = "cooldown"
        self.states.set_next_state(next_state)

@register_state
class Cooldown(BaseState):
    Name = "cooldown"
    DelayCount = 10
    Timeout = 15

    def enter(self, last_state, **kw):
        self.timer = Timer(self.DelayCount)

    def tick(self):
        if self.timer.expired:
            self.states.set_next_state("idle")
