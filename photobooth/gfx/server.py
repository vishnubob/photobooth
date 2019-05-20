from .. config import config
from .. base import Singleton
from . graphics import DisplayEngine
from multiprocessing.managers import BaseManager

class DisplayManager(BaseManager):
    pass

class DisplayControl(object):
    def init_engine(self):
        self.engine = DisplayEngine()
        self.engine.start()
        self.control = self.engine.control

    def show_text(self, text):
        self.control.show_text(text)

    def show_image(self, fn_img):
        self.contol.show_image(fn_img)

DisplayManager.register("DisplayControl", DisplayControl)

def run():
    address = (
        config["graphics"]["server_address"],
        config["graphics"]["port"]
    )
    authkey = config["graphics"]["authkey"].encode()
    man = DisplayManager(address=address, authkey=authkey)
    srv = man.get_server()
    srv.serve_forever()
