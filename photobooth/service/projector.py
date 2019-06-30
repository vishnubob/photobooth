import time
from .. config import config
from .. base import Singleton
from .. import bus

class ProjectorService(bus.Service):
    ServiceName = "Projector"

    def run(self):
        from .. projector import ProjectorControl
        self.running = True
        device = config["projector"]["device"]
        self.projector = ProjectorControl(device)
        self.projector.on()
        while self.running:
            time.sleep(.1)

    @bus.proxy
    def on(self):
        self.projector.on()

    @bus.proxy
    def off(self):
        self.projector.off()

def run(**kw):
    server = ProjectorService(serve=True)
    server.run()
