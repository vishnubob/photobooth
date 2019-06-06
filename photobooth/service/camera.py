import importlib
import time
from .. config import config
from .. import bus

class CameraService(bus.Service):
    ServiceName = "Camera"

    def build_camera(self):
        clspath = config["camera"]["class"]
        parts = clspath.split('.')
        (modpath, clsname) = (str.join('.', parts[:-1]), parts[-1])
        modpath = ".%s" % modpath
        mod = importlib.import_module(modpath, "photobooth")
        cls = getattr(mod, clsname)
        return cls()
    
    def run(self):
        self.camera = self.build_camera()
        self.running = True
        while self.running:
            time.sleep(1)

    @bus.proxy
    def capture(self):
        return self.camera.capture()

def run(**kw):
    service = CameraService(serve=True, **kw)
    service.run()
