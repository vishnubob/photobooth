import os
import importlib
from . timers import Timers
from . state import StateMachine
from . import keys
from . timers import Timer, Timers
from . config import config
from . display import DisplayService
from . import store


class Factory(object):
    def __init__(self, fn_config):
        config.load_config(fn_config)

    def build_camera(self):
        clspath = config["camera"]["class"]
        parts = clspath.split('.')
        (modpath, clsname) = (str.join('.', parts[:-1]), parts[-1])
        modpath = ".%s" % modpath
        mod = importlib.import_module(modpath, "photobooth")
        cls = getattr(mod, clsname)
        return cls()

    def build_datastore(self):
        return store.DataStore()

    def build_photobooth(self):
        camera = self.build_camera()
        datastore = self.build_datastore()
        booth = Photobooth(camera=camera, datastore=datastore)
        __builtins__["photobooth"] = booth
        keys.initialize()
        return booth

class Photobooth(object):
    def __init__(self, camera=None, datastore=None):
        self.timers = Timers()
        self.camera = camera
        self.datastore = datastore
        self.display = DisplayService()
        self.state = StateMachine()
        self.state.set_next_state("idle")
        self.running = False

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
