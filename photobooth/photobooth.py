import os
import importlib
from . base import Singleton
from . timers import Timers
from . state import StateMachine
from . import keys
from . timers import Timer, Timers
from . config import config
from . service import display, presence, camera, photolab
from . import store

class Photobooth(Singleton):
    def init_instance(self):
        self.timers = Timers()
        self.camera = camera.CameraService()
        self.datastore = store.DataStore()
        self.display = display.DisplayService()
        self.presence = presence.PresenceService()
        self.photolab = photolab.PhotolabService()
        self.state = StateMachine()
        self.state.set_next_state("idle")
        self.running = False
        __builtins__["photobooth"] = self

    def loop(self):
        self.timers.tick()
        self.state.tick()

    def run(self, rate=60):
        self.running = True
        timer = Timer(1 / rate)
        while self.running:
            self.loop()
            timer.wait()
            timer.reset()

def run(**kw):
    photobooth = Photobooth()
    photobooth.run()

