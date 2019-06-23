import logging
import os
import redis
from . config import config

__all__ = ["log", "debug", "info", "warning", "error", "critical"]
LogName = __name__.split('.')[0]

class LogReader(object):
    RedisHost = config["redis"]["host"]
    RedisDestination = config["log"]["redis_destination"]

    def __init__(self):
        self.destination = self.RedisDestination
        self.rds = redis.Redis(self.RedisHost)

    def run(self):
        loglen = self.rds.llen(self.destination)
        logs = self.rds.lrange(self.destination, 0, loglen)
        print(logs)

class RedisHandler(logging.Handler):
    RedisHost = config["redis"]["host"]
    RedisDestination = config["log"]["redis_destination"]

    def __init__(self):
        logging.Handler.__init__(self)
        self.destination = self.RedisDestination
        self.rds = redis.Redis(self.RedisHost)

    def emit(self, record):
        try:
            msg = self.format(record)
            pipe = self.rds.pipeline()
            pipe.lpush(self.destination, msg)
            #pipe.ltrim(self.destination, 0, 1000)
            pipe.execute()
        except Exception:
            self.handleError(record)

# root logger
logger = logging.getLogger(LogName)
logger.setLevel(config["log"]["level"])
formatter = logging.Formatter('%(asctime)s [%(levelname)s %(module)s:%(lineno)s]: %(message)s')

# log to standard error
slog = logging.StreamHandler()
slog.setLevel(config["log"]["level"])
slog.setFormatter(formatter)
logger.addHandler(slog)

# log to redis
rlog = RedisHandler()
rlog.setLevel(config["log"]["level"])
rlog.setFormatter(formatter)
logger.addHandler(rlog)

# log to file
try:
    flog = logging.FileHandler(config["log"]["filename"])
    flog.setLevel(config["log"]["level"])
    flog.setFormatter(formatter)
    logger.addHandler(flog)
except (PermissionError, FileNotFoundError) as err:
    msg = "Could not configure FileHandle logging: %s" % err
    logger.warning(msg)

# bind logger methods to the root of this module
log = logger.log
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
