import time

class Timer(object):
    def __init__(self, length=None):
        self.reset()
        self.length = length

    def reset(self):
        self.timestamp = time.time()

    @property
    def elapsed(self):
        return time.time() - self.timestamp

    @property
    def expired(self):
        if self.length is None:
            return False
        return self.elapsed >= self.length
    
    def wait(self):
        delta = max(0, self.length - self.elapsed)
        if not delta:
            return
        time.sleep(delta)
