import os
import time
import random
import threading
import pygame as pg
from pygame.locals import *
from .. base import Singleton

class EventHandler(object):
    def fire(self, event):
        msg = "Unhandled event code: %s" % event.type

class TimerHandler(EventHandler):
    def __init__(self, callback):
        self.callback = callback

    def fire(self, event):
        self.callback()

class EventManager(object):
    def __init__(self, event_map=None):
        self.event_map = event_map if event_map is not None else {}
        self.default_fire = EventHandler()

    def register(self, event_code, handler):
        self.event_map[event_code] = handler

    def fire(self, event):
        handler = self.event_map.get(event.type, self.default_fire)
        handler.fire(event)

class Canvas(object):
    DefaultResolution = (1280, 720)
    screen = None
    
    def __init__(self, frame_rate=60):
        self.frame_rate = frame_rate
        self.events = EventManager()
        self.init_pygame()
        
    def init_display_driver(self):
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))
        #drivers = ['fbcon', 'directfb', 'svgalib', 'x11']
        drivers = ['X11', 'dga', 'ggi','vgl','directfb', 'fbcon', 'svgalib']
        found = False
        for driver in drivers:
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pg.display.init()
            except pg.error:
                print('Driver: {0} failed.'.format(driver))
                continue
            found = True
            break
        if not found:
            raise Exception('No suitable video driver found!')
        modes = pg.display.list_modes()
        print(modes)
        #pg.display.set_mode(modes[0])
        #pg.display.set_mode(self.DefaultResolution, pg.RESIZABLE)
        pg.display.set_mode(self.DefaultResolution)
        #pg.display.toggle_fullscreen()
        
    def init_pygame(self):
        self.init_display_driver()
        self.size = (pg.display.Info().current_w, pg.display.Info().current_h)
        msg = "Framebuffer size: %d x %d" % (self.size[0], self.size[1])
        print(msg)
        self.screen = pg.display.set_mode(self.size, pg.FULLSCREEN)
        self.screen.fill((0, 0, 0))        
        pg.font.init()
        pg.display.update()
        pg.mouse.set_visible(False)
        self.clock = pg.time.Clock()

    def loop(self):
        self.clock.tick(self.frame_rate)
        for event in pg.event.get():
            self.events.fire(event)
        pg.display.update()
        fps = self.clock.get_fps()

class CountDown(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.font = pg.font.Font(None, 240)
        self.count = 3
        handler = TimerHandler(self.increment)
        self.canvas.events.register(USEREVENT, handler)
        self.timestamp = self.canvas.clock.get_rawtime()
        pg.time.set_timer(USEREVENT, 1000)

    def increment(self):
        self.timestamp = pg.time.get_ticks()
        self.count -= 1
        if self.count == 1:
            pg.time.set_timer(USEREVENT, 0)

    def draw(self):
        now = pg.time.get_ticks()
        tr = (now - self.timestamp) / 1000
        angle = 360 * tr
        scale = 25 * tr
        #print(self.count, angle, scale, now, self.timestamp)
        msg = str(self.count)
        surface = self.font.render(msg, True, pg.Color("dodgerblue"))
        surface = pg.transform.rotozoom(surface, angle, scale)
        screen_rect = self.canvas.screen.get_rect()
        rect = surface.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        self.canvas.screen.fill(pg.Color("red"))
        self.canvas.screen.blit(surface, rect)

class DisplayController(object):
    def __init__(self, canvas):
        self.canvas = canvas
        self.font = pg.font.Font(None, 240)
        self.buffer = pg.Surface(self.canvas.screen.get_size())
        self.buffer.fill(pg.Color("black"))
        self.refresh = None

    def display_image(self, fn_img):
        img = pg.image.load(fn_img)
        img = pg.transform.scale(img, self.canvas.size)
        screen_rect = self.canvas.screen.get_rect()
        rect = img.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        self.buffer.fill(pg.Color("red"))
        self.buffer.blit(img, rect)

    def display_text(self, text):
        surface = self.font.render(text, True, pg.Color("dodgerblue"))
        screen_rect = self.canvas.screen.get_rect()
        rect = surface.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        self.buffer.fill(pg.Color("black"))
        self.buffer.blit(surface, rect)

    def draw(self):
        if self.refresh:
            self.refresh()
            self.refresh = None
        rect = self.buffer.get_rect()
        self.canvas.screen.blit(self.buffer, rect)

class DisplayEngine(Singleton, threading.Thread):
    def __init__(self, *args, **kw):
        pass

    def init_instance(self, *args, **kw):
        super().__init__(*args, **kw)
        self.running = False
        self.daemon = True
        self.canvas = Canvas()
        self.control = DisplayController(self.canvas)
        self.start()

    def run(self):
        try:
            self.running = True
            while self.running:
                self.control.draw()
                self.canvas.loop()
        finally:
            pg.quit()

