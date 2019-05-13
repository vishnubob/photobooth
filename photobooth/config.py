import os
import logging

DefaultConfig = {
    "logfilename": "photobooth.log",
    "loglevel": logging.DEBUG,
}

class Config(dict):
    def __init__(self, **kw):
        self.update(DefaultConfig)
        self.update(kw)

config = Config()
