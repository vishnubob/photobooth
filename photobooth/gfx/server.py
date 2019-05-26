from .. config import config
from .. base import Singleton
from . graphics import DisplayEngine
from multiprocessing.managers import BaseManager

class DisplayManager(BaseManager):
    pass

class DisplayControl(object):
    def init_engine(self):
        self.engine = DisplayEngine()
        self.control = self.engine.control

    def show_text(self, text):
        self.control.show_text(text)

    def show_image(self, fn_img):
        self.control.show_image(fn_img)

class DummyControl(object):
    def init_engine(self):
        print("init_engine")

    def show_text(self, text):
        print("show_text", text)

    def show_image(self, fn_img):
        print("show_image", fn_img)

args = None

def get_mode():
    global args
    return args

DisplayManager.register("DummyControl", DummyControl)
DisplayManager.register("DisplayControl", DisplayControl)
DisplayManager.register("get_mode", get_mode)

def run(dummy=False):
    global args
    args = {"dummy": dummy}
    address = (
        config["graphics"]["server_address"],
        config["graphics"]["port"]
    )
    authkey = config["graphics"]["authkey"].encode()
    man = DisplayManager(address=address, authkey=authkey)
    srv = man.get_server()
    srv.serve_forever()
