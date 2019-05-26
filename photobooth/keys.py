import sys
import os
import termios
import atexit

from . base import Singleton

class KeyInput(Singleton):
    def init_instance(self):
        self.initialized = False

    def initialize(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        new_settings = self.old_settings[:]
        new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON)
        new_settings[6][termios.VMIN] = 0
        new_settings[6][termios.VTIME] = 0
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)
        self.initialized = True

    def terminate(self):
        if not self.initialized:
            return
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
        self.initialized = False

    def get(self):
        if not self.initialized:
            raise ValueError("KeyInput is not initialized!")
        ch_set = []
        ch = os.read(sys.stdin.fileno(), 1)
        while ch != None and len(ch) > 0:
            ch_set.append(chr(ch[0]))
            ch = os.read(sys.stdin.fileno(), 1)
        return ch_set

def initialize():
    key_input = KeyInput()
    key_input.initialize()

@atexit.register
def terminate():
    key_input = KeyInput()
    key_input.terminate()

def get_input():
    key_input = KeyInput()
    return key_input.get()

if __name__ == "__main__":
    key_input = KeyInput()
    key_input.initialize()
    while True:
        res = key_input.get()
        if res:
            print(res)
