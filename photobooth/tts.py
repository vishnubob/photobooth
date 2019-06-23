import pyttsx3

class TextToSpeech(object):
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

    @property
    def is_busy(self):
        return self.engine.isBusy()

    def speak(self, text):
        for line in text:
            self.engine.say(line)
            self.engine.runAndWait()
