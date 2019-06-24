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

    def capture(self, fn_target=None):
        img = self.camera.capture(copy=True, fn_target=fn_target)
        return img
