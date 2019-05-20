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
        self.control = self.man.DisplayControl()
        self.control.init_engine()
        self.show_text = self.control.show_text
        self.show_image = self.control.show_image
