import logging
import os
from . config import config

__all__ = ["log", "debug", "info", "warning", "error", "critical"]
LogName = __name__.split('.')[0]

class CallbackHandler(logging.Handler):
    def __init__(self, callback):
        logging.Handler.__init__(self)
        self.callback = callback

    def emit(self, record):
        try:
            msg = self.format(record)
            self.callback(msg)
        except Exception:
            self.handleError(record)

# root logger
logger = logging.getLogger(LogName)
logger.setLevel(config["loglevel"])
formatter = logging.Formatter('%(asctime)s [%(levelname)s %(module)s:%(lineno)s]: %(message)s')

# log to standard error
slog = logging.StreamHandler()
slog.setLevel(config["loglevel"])
slog.setFormatter(formatter)
logger.addHandler(slog)

# log to file
try:
    flog = logging.FileHandler(config["logfilename"])
    flog.setLevel(config["loglevel"])
    flog.setFormatter(formatter)
    logger.addHandler(flog)
except FileNotFoundError as err:
    msg = "Could not configure FileHandle logging: %s" % err
    logger.warning(msg)

# bind logger methods to the root of this module
log = logger.log
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
