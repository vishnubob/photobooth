import os
import time
import random
import pygame as pg
from pygame.locals import *


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
    screen = None
    
    def __init__(self, frame_rate=60):
        self.frame_rate = frame_rate
        self.events = EventManager()
        self.init_pygame()
        
    def init_display_driver(self):
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print("I'm running under X display = {0}".format(disp_no))
        drivers = ['x11', 'fbcon', 'directfb', 'svgalib']
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
        
    def init_pygame(self):
        self.init_display_driver()
        self.size = (pg.display.Info().current_w, pg.display.Info().current_h)
        msg = "Framebuffer size: %d x %d" % (self.size[0], self.size[1])
        print(msg)
        self.screen = pg.display.set_mode(self.size, pg.FULLSCREEN)
        self.screen.fill((0, 0, 0))        
        pg.font.init()
        pg.display.update()
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
        self.font = pg.font.Font(None, 48)
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
        print(self.count, angle, scale, now, self.timestamp)
        msg = str(self.count)
        surface = self.font.render(msg, True, pg.Color("dodgerblue"))
        surface = pg.transform.rotozoom(surface, angle, scale)
        screen_rect = self.canvas.screen.get_rect()
        rect = surface.get_rect(center=(screen_rect.centerx, screen_rect.centery))
        self.canvas.screen.fill(pg.Color("red"))
        self.canvas.screen.blit(surface, rect)

canvas = Canvas()
cd = CountDown(canvas)
while True:
    cd.draw()
    canvas.loop()
