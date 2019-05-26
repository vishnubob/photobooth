from .. config import config
from . server import DisplayManager
import time

class DisplayClient(object):
    def connect(self):
        address = (
            config["graphics"]["host"], 
            config["graphics"]["port"]
        )
        authkey = config["graphics"]["authkey"].encode()
        self.man = DisplayManager(address=address, authkey=authkey)
        while True:
            try:
                self.man.connect()
                break
            except ConnectionRefusedError:
                time.sleep(5)
        mode = self.man.get_mode()._getvalue()
        if mode["dummy"]:
            self.control = self.man.DummyControl()
        else:
            self.control = self.man.DisplayControl()
        self.control.init_engine()

    def call(self, func):
        func()

    def show_text(self, *args, **kw):
        func = lambda: self.control.show_text(*args, **kw)
        self.call(func)

    def show_image(self, *args, **kw):
        func = lambda: self.control.show_image(*args, **kw)
        self.call(func)
