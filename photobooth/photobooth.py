import os
from . state import StateMachine
from . import keys
from . timer import Timer
from . config import config
from . import gfx

keys.initialize()

class Factory(object):
    def __init__(self, fn_config):
        config.load_config(fn_config)

    def init_paths(self):
        dirs = self.config["paths"].copy()
        dir_root = self.config["paths"]["root"]
        if not os.path.isdir(dir_root):
            os.makedirs(dir_root)
        del dirs["root"]
        for (name, dir_path) in dirs.items():
            if not os.path.abspath(dir_path):
                dir_path = os.path.join(dir_root, dir_path)
            if not os.path.isdir(dir_path):
                os.makedirs(dir_path)
            self.config[paths][name] = dir_path

    def build_photobooth(self):
        booth = Photobooth()
        __builtins__["photobooth"] = booth
        return booth

class Photobooth(object):
    def __init__(self):
        self.state = StateMachine()
        self.state.enter("idle")
        self.display = gfx.client.DisplayClient()
        self.display.connect()
        self.running = False

    def loop(self):
        self.state.tick()

    def run(self, rate=60):
        self.running = True
        timer = Timer(1 / rate)
        while self.running:
            self.loop()
            timer.wait()
            timer.reset()

