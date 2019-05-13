import time
from logger import *

class EventManager(object):
    def __init__(self):
        self.handlers = {}

    def fire(self, event):
        msg = "Event '%s' fired" % event.type

    def add_handler(self, event_type, handler):
        self.handlers[event_type].append(handler)

class Event(object):
    def __init__(self, *args, **kw):
        self.type = self.__class__.__name__

class EventHandler(object):
    def handle(self, event):
        pass

class StartEvent(Event):
    pass

