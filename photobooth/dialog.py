import random
import jellyfish
from . config import config

class SpeechWriter(object):
    Dialog = config["dialog"]["scripts"]
    Sentences = config["dialog"]["sentences"]

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

class SpeechDecoder(object):
    Choices = config["dialog"]["choices"]
    Weights = {  
        "soundex": 0.2,
        "match_rating_codex": 0.2,
        "metaphone": 0.7,
        "nysiis": 0.1
    }

    def __init__(self, choices=Choices):
        self.choices = choices

    def measure_one(self, test, target, algorithm):
        weight = self.Weights[algorithm]
        func = getattr(jellyfish, algorithm)
        test_phone = func(test)
        target_phone = func(target)
        score = jellyfish.damerau_levenshtein_distance(test_phone, target_phone)
        return score * weight

    def measure(self, test, target):
        if test == target:
            return 0
        scores = [self.measure_one(test, target, al) for al in self.Weights]
        return sum(scores)

    def best_score(self, spoken, aliases):
        words = spoken.split(' ')
        scores = []
        for word in words:
            sc = [self.measure(word, alias) for alias in aliases]
            scores += sc
        return min(scores)

    def decode(self, spoken, key):
        choices = self.choices[key]
        best_choice = None
        results = []
        for choice in choices:
            aliases = choices[choice]
            result = (choice, self.best_score(spoken, aliases))
            results.append(result)
        results.sort(key=lambda it: it[0])
        return results
