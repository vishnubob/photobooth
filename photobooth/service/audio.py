import time
from .. config import config
from .. base import Singleton
from .. import bus
from .. logger import *
from .. dialog import SpeechWriter

class AudioService(bus.Service):
    ServiceName = "AudioService"

    def run(self):
        from .. tts import TextToSpeech
        self.engine = TextToSpeech()
        self.dialog = SpeechWriter()
        while 1:
            time.sleep(1)

    @bus.proxy
    def speak_dialog(self, topic):
        msg = "speaking dialog '%s'" % topic
        debug(msg)
        text = self.dialog.get_script(topic)
        return self.engine.speak(text)

    @bus.proxy
    def speak(self, text):
        msg = "speaking '%s'" % text
        debug(msg)
        if type(text) is str:
            text = [text]
        return self.engine.speak(text)

def run(**kw):
    server = AudioService(serve=True)
    server.run()
