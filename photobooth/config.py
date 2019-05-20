import os
import json
import logging

DefaultConfig = {
    "log": {
        "filename": "photobooth.log",
        "level": logging.DEBUG,
    }
}

class Config(dict):
    def __init__(self, **kw):
        self.update(DefaultConfig)
        self.update(kw)

    def load_config(self, fn_config):
        with open(fn_config) as fh:
            cfg = json.load(fh)
        cfg = cfg["photobooth"]
        self.update(cfg)

config = Config()
