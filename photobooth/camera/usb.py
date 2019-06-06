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
        prefix = self.datastore.get_path("negatives")
        img = self.camera.capture(copy=True, prefix=prefix)
        return img
