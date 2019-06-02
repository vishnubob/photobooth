import sys
import time
import redis
import json
import pickle
import uuid
import threading

from tblib import pickling_support
pickling_support.install()

from . base import Singleton
#from photobooth.base import Singleton

class MessageBus(Singleton):
    RedisHost = "192.168.1.3"

    def init_instance(self):
        self.rds = redis.Redis(self.RedisHost)
        self.bus = self.rds.pubsub()
        self.channels = {}
        self.thread = None

    def start_thread(self, daemon=True):
        assert self.thread is None
        self.thread = self.bus.run_in_thread(sleep_time=0.001, daemon=daemon)

    def stop_thread(self):
        assert self.thread is not None
        self.thread.stop()
        self.thread.join()
        self.thread = None

    def is_thread_running(self):
        return self.thread is not None

    def publish(self, channel, data):
        #print("publish", channel, data)
        data = pickle.dumps(data)
        self.rds.publish(channel, data)

    def register(self, channel, handler):
        def wrapper(message):
            message["channel"] = message["channel"].decode()
            message["data"] = pickle.loads(message["data"])
            handler(message)
        sub = {channel: wrapper}
        self.channels.update(sub)
        running = self.is_thread_running()
        if running:
            self.stop_thread()
        self.bus.subscribe(**self.channels)
        #print(self.bus.channels)
        if running:
            self.start_thread()
        return handler

def handler(handler, channel=None):
    if channel is None:
        (prefix, *channel) = handler.__name__.split('_')
        assert prefix == "handle"
        channel = str.join('_', channel)
    bus = MessageBus()
    return bus.register(channel, handler)

def publish(channel, msg):
    bus = MessageBus()
    bus.publish(channel, msg)

def start_thread():
    bus = MessageBus()
    bus.start_thread()

def stop_thread():
    bus = MessageBus()
    bus.stop_thread()

class ReturnObject(object):
    def __init__(self, return_channel):
        self.return_channel = return_channel
        self.uid = str(uuid.uuid4())
        self.event = threading.Event()
        self._value = None

    @property
    def receipt(self):
        desc = {
            "return_channel": self.return_channel,
            "return_uid": self.uid
        }
        return desc

    @property
    def is_ready(self):
        return self.event.is_set()

    def get_value(self):
        assert self.event.is_set()
        if isinstance(self._value, Exception):
            self._value.raise_exc()
        return self._value

    def set_value(self, value):
        self._value = value
        self.event.set()

    value = property(get_value, set_value)

    def wait(self, timeout=None):
        ok = self.event.wait()
        if not ok:
            raise TimeoutError
        return self.value

    def poll(self):
        return self.is_ready

class ReturnException(Exception):
    def __init__(self, exc):
        self.exc = exc
        self.tb = sys.exc_info()[2]

    def raise_exc(self):
        raise self.exc.with_traceback(self.tb)

class ReturnManager(Singleton):
    def init_instance(self):
        self.waiters = {}
        self.return_uid = str(uuid.uuid4())
        self.return_channel = "return-%s" % self.return_uid
        self.bus = MessageBus()
        self.bus.register(self.return_channel, self.handle_return)
        self.lock = threading.Lock()

    def handle_return(self, msg):
        return_uid = msg["data"]["return_uid"]
        return_value = msg["data"]["return_value"]
        self.lock.acquire()
        ro = self.waiters[return_uid]
        del self.waiters[return_uid]
        self.lock.release()
        ro.value = return_value

    def new_handler(self):
        ro = ReturnObject(self.return_channel)
        self.lock.acquire()
        self.waiters[ro.uid] = ro
        self.lock.release()
        return ro

class Service(Singleton):
    ServiceName = "BaseService"
    CallTable = {}

    class Proxy(object):
        def __init__(self, service):
            self.service = service

        def __getattr__(self, attr):
            def wrapper(*args, **kw):
                return self.service.proxy_call(attr, *args, **kw)
            return wrapper

    def init_instance(self, serve=False):
        self.bus = MessageBus()
        if not self.bus.is_thread_running():
            self.bus.start_thread()
        self.return_manager = ReturnManager()
        self.service_uid = str(uuid.uuid4())
        self.channel_name = "%s-calls" % self.ServiceName
        if serve:
            self.serve()

    @property
    def _proxy(self):
        return self.Proxy(self)
    
    @classmethod
    def proxy(cls, call):
        return call

    def serve(self):
        self.bus.register(self.channel_name, self.handle_call)

    def handle_call(self, message):
        data = message["data"]
        func_name = data["func_name"]
        args = data["args"]
        kwargs = data["kwargs"]
        func = getattr(self, func_name)
        try:
            ret = func.wrapper(*args, **kwargs)
        except BaseException as err:
            ret = ReturnException(err)
        data["return_value"] = ret
        return_channel = data["return_channel"]
        publish(return_channel, data)

    def proxy_call(self, func_name, *args, **kwargs):
        ro = self.return_manager.new_handler()
        data = {
            "func_name": func_name,
            "args": args,
            "kwargs": kwargs,
        }
        data.update(ro.receipt)
        publish(self.channel_name, data)
        return ro

def proxy(call):
    class ProxyCall(object):
        class CallRouter(object):
            def __init__(self, obj, func):
                self.obj = obj
                self.func_name = func.__name__
                self.wrapper = lambda *args, **kw: func(obj, *args, **kw)

            def __call__(self, *args, **kwargs):
                return self.obj.proxy_call(self.func_name, *args, **kwargs)

        def __init__(self, func):
            self.func = func

        def __get__(self, obj, objtype=None):
            return self.CallRouter(obj, self.func)
    return ProxyCall(call)
