import time
from collections import defaultdict
from . logger import *
from . base import Singleton

class EventManager(Singleton):
    def init_instance(self):
        self.handlers = defaultdict(list)

    def fire(self, event):
        if not isinstance(event, Event):
            raise TypeError("name must be an instance of Event class")
        msg = "'%s' fired" % event
        debug(msg)
        handlers = self.handlers.get(event.name)
        if not handlers:
            return
        for callback in handlers:
            callback(event)

    def add_handler(self, name=None, callback=None):
        if name is None:
            raise ValueError("name required")
        if type(name) != str:
            raise TypeError("name must be string")
        if callback is None:
            raise ValueError("callback required")
        if not callable(callback):
            raise TypeError("callback must be a callable")
        self.handlers[name].append(callback)

    def remove_handler(self, name=None, callback=None):
        if name is None:
            raise ValueError("name required")
        if callback is None:
            raise ValueError("callback required")
        if type(name) != str:
            raise TypeError("name must be string")
        if not callable(callback):
            raise TypeError("callback must be a callable")
        if name not in self.handlers:
            raise KeyError("unknown event '%s'" % name)
        callbacks = self.handlers.get(name)
        if not callbacks:
            return
        idx = callbacks.index(callback)
        if idx >= 0:
            del callbacks[idx]
        if len(callbacks) == 0:
            del self.handlers[name]

class Event(object):
    def __init__(self, name=None, data=None):
        if name is None:
            raise ValueError("name required")
        if type(name) != str:
            raise TypeError("name must be string")
        self.name = name
        self.data = data
        self.timestamp = time.time()

    def fire(self):
        manager = EventManager()
        manager.fire(self)

def fire(*args, **kw):
    ev = Event(*args, **kw)
    ev.fire()
