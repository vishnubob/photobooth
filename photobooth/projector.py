import serial
import time
from . logger import *

class ProjectorControl(object):
    DefaultBaud = 9600

    def __init__(self, port, projector_id=0):
        self.projector = serial.Serial(port, self.DefaultBaud)
        self.projector_id = projector_id

    def get_response(self):
        resp = b''
        while self.projector.in_waiting:
            resp += self.projector.read(1)
            time.sleep(.1)
        return resp.decode()

    def command(self, cmd):
        cmd = "~%02d00 %s\r" % (self.projector_id, cmd)
        self.projector.write(cmd.encode())
        return cmd

    def on(self):
        msg = "Projector on"
        info(msg)
        self.command("1")

    def off(self):
        msg = "Projector off"
        info(msg)
        self.command("0")
