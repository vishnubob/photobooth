from .. config import config
from .. base import Singleton
from .. import bus
from .. display import DisplayEngine

class DisplayService(bus.Service):
    ServiceName = "Display"

    def run(self):
        self.engine = DisplayEngine()
        self.control = self.engine.control
        self.engine.run()

    @bus.proxy
    def display_text(self, text):
        self.control.display_text(text)

    @bus.proxy
    def display_image(self, fn_img):
        self.control.display_image(fn_img)

def run(**kw):
    server = DisplayService(serve=True)
    server.run()
