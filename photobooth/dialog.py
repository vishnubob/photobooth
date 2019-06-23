import random

Dialog = {
    "greetings": [
        "hello",
        "greetings",
        "greetings and salutations",
        "hi there",
        "welcome",
        "hey good looking"
    ],
    "processing": [
        "processing, please wait",
        "developing your photo",
        "please wait while I process your photo"
    ],
    "introduction": [
        "i am a photobooth",
        "i am a computerized photographer",
        "i want to take your picture",
        "i am not staring at you.  i am a cyborg photographer.  just act natural.  this is a candid shot."
    ],
    "ready": [
        "when you are ready, say ready, and i will take your picture"
    ],
    "bored": [
        "ready or not, here we go"
    ],
    "background": [
        "please speak the name of the background you would like to appear in front of."
    ],
    "shy": [
        "either you are shy and did not say anything, or i did not hear you"
    ],
    "appraisal": [
        "i think this is the best photograph i have ever taken",
        "you look absolutely beautiful",
        "what an amazing picture",
        "wow! this should hang in a museum",
        "one word. amazing.",
        "eat your heart out, ansel adams"
    ]
}

Sentences = {
    "introduction": ["greetings", "introduction"],
    "ready": ["ready"],
    "bored": ["bored"],
    "background": ["background"],
    "shy": ["shy"],
    "processing": ["processing"],
    "appraisal": ["appraisal"],
}

class SpeechWriter(object):
    def __init__(self, dialog_map=Dialog, sentence_map=Sentences):
        self.dialog_map = dialog_map
        self.sentence_map = sentence_map

    def build(self, topic):
        structure = self.sentence_map[topic]
        for element in structure:
            choices = self.dialog_map[element]
            choice = random.choice(choices)
            for line in choice.split('.'):
                line = line.strip()
                if not line:
                    continue
                yield line

    def get_script(self, topic):
        text = list(self.build(topic))
        return text
