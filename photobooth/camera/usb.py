import os
from . base import BaseCamera
from . drivers import gphoto
from .. events import fire
from .. config import config
from .. store import DataStore
from .. timers import Timers

class USBCamera(BaseCamera):
    def __init__(self, camera_name=None):
        api = gphoto.Camera()
        self.camera = api.open(camera_name)
        self.datastore = DataStore()
        self.timers = Timers()

    def capture(self):
        img = self.camera.capture(copy=True, prefix=self.datastore.get_path("negatives"))
        self.image_fn = os.path.split(img)[-1]
        self.timers.set_timeout(.1, self.captured)

    def captured(self):
        data = {"success": True, "image_filename": self.image_fn}
        fire("capture", data)
