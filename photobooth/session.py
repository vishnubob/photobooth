import time
import uuid
from datetime import datetime
import os
from . base import Singleton
from . store import DataStore

def new_session_id():
    return str(uuid.uuid4()).split('-')[0]

class Session(object):
    def __init__(self, session_id=None):
        self.session_id = session_id if session_id is not None else new_session_id()
        self.timestamp_begin = datetime.now()
        self.day_str = self.timestamp_begin.strftime("%A, %B %d")
        self.time_str = self.timestamp_begin.strftime("%-I:%m %p")
        self.image_count = 0
        self.session_id = session_id
        self.data_store = DataStore()
        root = os.path.join(self.day_str, self.time_str)
        self.path_captures = self.data_store.new_path("session", self.day_str, self.time_str, "captures")
        self.path_processed = self.data_store.new_path("session", self.day_str, self.time_str, "processed")

    def inc_image(self):
        self.image_count += 1
        return self.image_count

    @property
    def capture_path(self):
        fn_capture = "capture-%04d.jpg" % self.image_count
        fn_capture = os.path.join(self.path_captures, fn_capture)
        return fn_capture

    @property
    def processed_path(self):
        fn_processed = "processed-%04d.jpg" % self.image_count
        fn_processed = os.path.join(self.path_processed, fn_processed)
        return fn_processed

    def close(self):
        self.timestamp_finish = time.time()
