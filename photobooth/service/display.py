from .. config import config
from .. base import Singleton
from .. import bus

class DisplayService(bus.Service):
    ServiceName = "Display"

    def run(self):
        from .. display import DisplayEngine
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
