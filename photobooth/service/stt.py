import time
from .. config import config
from .. base import Singleton
from .. import bus

class SpeechToTextService(bus.Service):
    ServiceName = "SpeechToText"

    def run(self):
        from .. stt import SpeechToText
        self.engine = SpeechToText()
        while 1:
            time.sleep(1)

    @bus.proxy
    def listen(self):
        return self.engine.listen()

def run(**kw):
    server = SpeechToTextService(serve=True)
    server.run()