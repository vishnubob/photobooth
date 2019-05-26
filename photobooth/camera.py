from . events import fire
from . config import config
from . timers import Timers

class BaseCamera(object):
    def __init__(self, dir_images="."):
        self.dir_images = dir_images

    def capture(self):
        pass

class MockCamera(Camera):
    def __init__(self):
        self.mock_image = self.config["camera"]["mock_image"]
        self.counter = 0
        self.timers = Timers()

    def capture(self):
        self.timers.set_timeout(2, self.captured)

    def captured(self):
        fn_img = "IMG-%04d.jpg" % self.counter
        fn_img = os.path.join(self.dir_images, img_fn)
        os.copyfile(self.mock_image, img_fn)
        data = {"success": True, "filename": fn_img)
        fire("capture", data)
