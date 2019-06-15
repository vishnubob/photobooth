from .. config import config
from .. import bus

import threading
import math
import time

class PresenceService(bus.Service):
    ServiceName = "Presence"

    def init_instance(self, driver="dummy", impulse=0.5, **kw):
        super().init_instance(**kw)
        self.impulse = impulse
        self.decay = Decay()
        self.running = False
        if driver == "dummy":
            self.driver = PresenceDriverDummy(service=self)
        elif driver == "pir":
            self.driver = PresenceDriverPIR(service=self)
        else:
            msg = "unknown presence driver '%s'" % driver
            raise ValueError(msg)

    def run(self):
        self.running = True
        while self.running:
            time.sleep(1)

    def impulse_callback(self):
        self.decay += self.impulse

    @bus.proxy
    def exit(self):
        self.running = False

    @bus.proxy
    def check_presence(self):
        return bool(self.decay)

class Decay(object):
    def __init__(self, initial=0, halflife=-.1, threshold=.5, maxval=10):
        self.halflife = halflife
        self.maxval = maxval
        self.threshold = threshold
        self.reset(initial)

    def reset(self, initial):
        self.initial = initial
        self.timestamp = time.time()

    @property
    def value(self):
        now = time.time()
        delta = now - self.timestamp
        value = self.initial * math.e ** (delta * self.halflife)
        return value

    def __add__(self, value):
        self.initial = min(self.maxval, (self.value + value))
        self.timestamp = time.time()
        return self

    def __bool__(self):
        return self.value > self.threshold

class PresenceDriverBase(object):
    def __init__(self, service=None):
        self.service = service

class PresenceDriverDummy(PresenceDriverBase):
    class InputThread(threading.Thread):
        def __init__(self, callback, daemon=True, rate=60):
            super().__init__()
            self.callback = callback
            self.sleep_time = 1 / rate
            self.daemon = True
            self.running = False

        def run(self):
            from .. import keys
            keys.initialize()
            self.running = True
            while self.running:
                keys_input = keys.get_input()
                if len(keys_input) > 0:
                    self.callback()
                time.sleep(self.sleep_time)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.thread = self.InputThread(self.service.impulse_callback)
        self.thread.start()

class PresenceDriverPIR(PresenceDriverBase):
    def __init__(self, **kw):
        super().__init__(**kw)
        import pigpio
        self.pi = pigpio.pi()
        self.pir_gpio = 17
        self.cb_id = self.pi.callback(self.pir_gpio, pigpio.RISING_EDGE, self.presence_callback)

    def presence_callback(self, gpio, level, tick):
        if level == 1:
            self.service.impulse_callback()

def run(**kw):
    service = PresenceService(serve=True, **kw)
    service.run()
