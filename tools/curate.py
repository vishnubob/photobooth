import os
import shutil
import json
import sys
import subprocess
import time
from imgops import resize_and_crop
from PIL import Image
import termios
import atexit
from collections import defaultdict
from google_images_download import google_images_download

def prompt(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def download(keyword, offset=0, **kw):
    print("offset", offset)
    images = google_images_download.googleimagesdownload()
    args = {
        "keywords": keyword,
        "limit": max(1, offset),
        "silent_mode": True,
        "size": ">2MP",
        "aspect": "wide",
        "offset": offset
    }
    args.update(kw)
    paths = images.download(args)
    return paths[0][keyword][0]

rint = lambda val: int(round(val))

def crop(img, target_size=None):
    old_size = img.size
    left = (old_size[0] - target_size[0]) / 2
    top = (old_size[1] - target_size[1]) / 2
    right = old_size[0] - left
    bottom = old_size[1] - top
    rect = [rint(x) for x in (left, top, right, bottom)]
    crop = img.crop(rect)
    return crop

def resize(img, target_size=None, scale=None, resample=Image.LANCZOS):
    img_size = img.size
    if target_size == None:
        assert 1 >= scale >= 0
        target_size = [
            rint(img_size[0] * scale),
            rint(img_size[1] * scale)
        ]
    ratio = max(target_size[0] / img_size[0], target_size[1] / img_size[1])
    new_size = [
        int(round(img_size[0] * ratio)),
        int(round(img_size[1] * ratio))
    ]
    return img.resize(new_size, resample)

def resize_and_crop(img, target_size=None, scale=None, resample=Image.LANCZOS):
    img = resize(img, target_size, scale, resample)
    if (img.size != target_size):
        img = crop(img, target_size)
    return img

class KeyInput(object):
    def __init__(self):
        self.initialized = False

    def initialize(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        new_settings = self.old_settings[:]
        new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)
        new_settings[6][termios.VMIN] = 0
        new_settings[6][termios.VTIME] = 0
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        self.initialized = True

    def terminate(self):
        if not self.initialized:
            return
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        self.initialized = False

    def get_on_enter(self):
        val = ''
        while True:
            ch = self.get()
            if ch == b'\n':
                sys.stdout.write('\n')
                sys.stdout.flush()
                break
            ch = ch.decode()
            sys.stdout.write(ch)
            sys.stdout.flush()
            val += ch
        return val

    def get(self):
        if not self.initialized:
            raise ValueError("KeyInput is not initialized!")
        while True:
            ch = os.read(sys.stdin.fileno(), 1)
            if ch:
                break
            time.sleep(.01)
        return ch
    
    def get_char(self):
        return self.get().decode()

class Logbook(object):
    def __init__(self, logbook=None):
        self.offsets = defaultdict(int)
        self.topics = set(["general"])
        if logbook != None:
            self.offsets.update(logbook.get("offsets", dict()))
            self.topics.update(logbook.get("topics", list()))

    def set_offset(self, keyword, offset):
        self.offsets[keyword] = offset

    def get_offset(self, keyword):
        return max(1, self.offsets[keyword])

    def add_topic(self, topic):
        self.topics.add(topic)

    def get_topics(self):
        return list(self.topics)

    def match_topic(self, keys):
        matches = []
        keys = set(keys)
        for topic in self.topics:
            if not keys.intersection(set(topic)):
                continue
            matches.append(topic)
        return matches

    def as_dict(self):
        logbook = {
            "offsets": dict(self.offsets),
            "topics": list(self.topics)
        }
        return logbook

class CurateImages(object):
    def __init__(self, source_dir="downloads", out_dir="curated", resolution=(1280, 720), logbook="logbook.json"):
        self.source_dir = source_dir
        self.out_dir = out_dir
        self.resolution = resolution
        self.init_logbook(logbook)
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)

    def init_logbook(self, logbook):
        self.fn_logbook = logbook
        if os.path.exists(self.fn_logbook):
            with open(self.fn_logbook) as fh:
                logbook = json.load(fh)
            self.logbook = Logbook(logbook)
        else:
            self.logbook = Logbook()

    def save_logbook(self):
        logbook = self.logbook.as_dict()
        if not logbook:
            return
        with open(self.fn_logbook, 'w') as fh:
            json.dump(self.logbook.as_dict(), fh)

    def walk(self):
        for (root, dirs, files) in os.walk(self.source_dir):
            for fn in files:
                yield os.path.join(root, fn)

    def display(self, img):
        ext = img.split('.')[-1]
        imgfn = "display.%s" % ext
        img = Image.open(img)
        img = resize_and_crop(img, target_size=self.resolution)
        img.save(imgfn)
        cmd = ["display", imgfn]
        proc = subprocess.Popen(cmd)
        return (proc, imgfn)

    def get_keyword(self):
        keys.terminate()
        prompt('keyword > ')
        keyword = input()
        keys.initialize()
        return keyword

    def get_new_topic(self):
        keys.terminate()
        prompt('\nnew topic > ')
        topic = input()
        keys.initialize()
        return topic

    def get_name(self):
        keys.terminate()
        prompt('name > ')
        name = input()
        keys.initialize()
        return name

    def save_image(self, path, name, topic):
        ext = path.split('.')[-1].lower()
        out_dir = os.path.join(self.out_dir, topic)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        target = "%s.%s" % (name, ext)
        target = os.path.join(out_dir, target)
        shutil.copyfile(path, target)

    def loop(self):
        if self.state == "initial":
            prompt("(k)eyword (q)uit\n")
            cmd = keys.get_char()
            if cmd == 'k':
                self.state = "get_keyword"
            elif cmd == 'q':
                return False
        elif self.state == "get_keyword":
            self.keyword = self.get_keyword()
            self.state = "keyword"
        elif self.state == "get_topic":
            topics = str.join(', ', self.logbook.topics)
            msg = "Topics: %s\n(N)ew topic\ntopic > " % topics
            prompt(msg)
            chars = []
            while True:
                ch = keys.get().decode()
                prompt(ch)
                if ch == 'N':
                    self.topic = self.get_new_topic()
                    self.logbook.add_topic(self.topic)
                    self.state = "get_name"
                    break
                chars.append(ch)
                topics = self.logbook.match_topic(chars)
                if len(topics) == 0:
                    prompt("No matching topics!")
                    break
                elif len(topics) == 1:
                    self.topic = topics[0]
                    msg = "\nTopic: %s\n" % self.topic
                    prompt(msg)
                    self.state = "get_name"
                    break
        elif self.state == "get_name":
            name = self.get_name()
            self.save_image(self.path, name, self.topic)
            self.state = "keyword"
        elif self.state == "keyword":
            offset = self.logbook.get_offset(self.keyword)
            self.path = download(self.keyword, offset=offset)
            self.logbook.set_offset(self.keyword, offset + 1)
            (proc, imgfn) = self.display(self.path)
            prompt("(k)eyword (s)ave (n)ext (q)uit\n")
            cmd = keys.get_char()
            os.unlink(imgfn)
            proc.kill()
            proc.wait()
            if cmd == 'k':
                self.state = "get_keyword"
            elif cmd == 's':
                self.state = "get_topic"
            elif cmd == 'n':
                return True
            elif cmd == 'q':
                return False
        else:
            assert 0
        return True

    def run(self):
        run = True
        self.state = "initial"
        while run:
            run = self.loop()

keys = KeyInput()

if __name__== "__main__":
    curator = CurateImages()
    keys.initialize()
    try:
        curator.run()
    finally:
        curator.save_logbook()
        keys.terminate()
