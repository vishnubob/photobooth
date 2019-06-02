from .. config import config
from .. base import Singleton
from .. import bus
from . graphics import DisplayEngine

class DisplayServer(Singleton):
    def init_instance(self):
        self.engine = DisplayEngine()
        self.control = self.engine.control
        bus.handler(self.handle_display_text)
        bus.handler(self.handle_display_image)

    def run(self):
        self.engine.run()

    def handle_display_text(self, msg):
        text = msg["data"]
        self.control.display_text(text)

    def handle_display_image(self, msg):
        fn_img = msg["data"]
        self.control.display_image(fn_img)

def run(**kw):
    server = DisplayServer()
    bus.start_thread()
    server.run()
