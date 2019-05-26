import os
from . base import BaseCamera
from .. events import fire
from .. config import config
from .. timers import Timers
from .. store import DataStore

class MockCamera(BaseCamera):
    def __init__(self):
        self.store = DataStore()
        self.mock_image = config["camera"]["mock_image"]
        self.counter = 0
        self.timers = Timers()

    def capture(self):
        self.timers.set_timeout(2, self.captured)

    def captured(self):
        fn_img = "IMG-%04d.jpg" % self.counter
        self.counter += 1
        self.store.copyinto(self.mock_image, "negatives", filename=fn_img)
        data = {"success": True, "image_filename": fn_img}
        fire("capture", data)
