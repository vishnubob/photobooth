from . state import StateMachine
from . import keys
from . timer import Timer

keys.initialize()

class Photobooth(object):
    def __init__(self):
        self.state = StateMachine()
        self.state.enter("idle")
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

