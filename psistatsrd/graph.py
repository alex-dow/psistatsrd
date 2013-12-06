import pygame
import numpy as np
from pygame.locals import *
import random
import math

class Graph(object):

    SCROLL_TOP = 1
    SCROLL_BOTTOM = 2

    def __init__(self, *args, **kwargs):
        self.bgcolor      = kwargs["bgcolor"] if "bgcolor" in kwargs else (30,30,30)
        self.text_bgcolor = kwargs["text_bgcolor"] if "text_bgcolor" in kwargs else (0,0,0)
        self.color        = kwargs["color"] if "color" in kwargs else (255,255,255)
        self.text_color   = kwargs["text_color"] if "text_color" in kwargs else (255,255,255)
        self.line_width   = kwargs['line_width'] if 'line_width' in kwargs else 1
        self.line_aa      = kwargs['line_aa'] if 'line_aa' in kwargs else False
        self.width        = kwargs['width'] if 'width' in kwargs else 50
        self.height       = kwargs['height'] if 'height' in kwargs else 20
        self.interpolate  = kwargs['interpolate'] if 'interpolate' in kwargs else 10
        self.max_numbers  = kwargs['max_numbers'] if 'max_numbers' in kwargs else 20
        self.title        = kwargs['title'] if 'title' in kwargs else ""
        self.scroll_speed = kwargs['scroll_speed'] if 'scroll_speed' in kwargs else 1
        self.scroll_pause = kwargs['scroll_pause'] if 'scroll_pause' in kwargs else 20
        self.scroll_delay = kwargs['scroll_delay'] if 'scroll_delay' in kwargs else 25
        self.title_font   = kwargs['title_font'] if 'title_font' in kwargs else "monospace"
        self.title_size   = kwargs['title_size'] if 'title_size' in kwargs else 8
        self.graph_width  = kwargs['graph_width'] if 'graph_width' in kwargs else 0.7
        self.title_aa     = kwargs['title_aa'] if 'title_aa' in kwargs else True
        self.title_idx    = 0
        self.title_len    = 0

        if isinstance(self.title, list):
            self.current_title = self.title[self.title_idx]
            self.title_len = len(self.title)
        else:
            self.current_title = self.title

        self.text_xpos   = 0
        self.text_ypos   = self.height - self.scroll_delay
        self.text_pause  = 0

        self.scroll_pos = Graph.SCROLL_TOP

        self.surface = pygame.Surface((self.width, self.height))


        self.graph_surface = pygame.Surface((math.ceil(self.width * self.graph_width), self.height))

        try:
            with open('%s.ttf' % self.title_font):
                self.font = pygame.font.Font('%s.ttf' % self.title_font, self.title_size)
        except IOError:
            self.font = pygame.font.SysFont(self.title_font, self.title_size)

        self.title_surface = self.font.render(self.current_title, self.title_aa, self.text_color, self.text_bgcolor)


        self.ypos_mid = math.ceil(self.height / 2)

        self.graph = [0]
        self.numbers = [1]
        self.plot_queue = [0] * self.graph_surface.get_width()


        self.title_height = self.title_surface.get_height()
        self.ypos_mid = math.ceil(self.height / 2) - math.ceil(self.title_height / 2)


    def process(self, number):
        self.numbers.append(number)
        self.graph.extend(np.linspace(self.numbers[-2], self.numbers[-1], self.interpolate).tolist())
        if (len(self.numbers) == self.max_numbers):
            self.numbers = self.numbers[1:]

    def draw(self):
        if len(self.graph) == 0:
            return

        self.plot_queue = self.plot_queue[1:]
        self.plot_queue.append(self.graph[0])
        self.graph = self.graph[1:]
        
        plots = []

        for idx, plot in enumerate(self.plot_queue):
            plots.append((idx, (self.graph_surface.get_height() - (plot * self.graph_surface.get_height()))))

        self.graph_surface.fill(self.bgcolor)
        if self.line_aa == False:
            pygame.draw.lines(self.graph_surface, self.color, False, plots, self.line_width)
        else:
            pygame.draw.aalines(self.graph_surface, self.color, False, plots, self.line_width)
        
        if self.text_ypos >= self.ypos_mid and self.scroll_pos == Graph.SCROLL_TOP:
            if self.text_pause < self.scroll_pause:
                self.text_pause = self.text_pause + 1
            else:
                self.text_pause = 0
                self.scroll_pos = Graph.SCROLL_BOTTOM
                self.text_ypos = self.text_ypos + self.scroll_speed
        else:
            if self.text_ypos > (self.height + self.scroll_delay):
                self.text_ypos = -self.scroll_delay + -self.title_height
                self.scroll_pos = Graph.SCROLL_TOP
                if self.title_len > 0:
                    self.title_idx = self.title_idx + 1
                    if self.title_idx == self.title_len:
                        self.title_idx = 0
                    self.current_title = self.title[self.title_idx]
                
                self.title_surface = self.font.render(self.current_title, self.title_aa, self.text_color)
            
            self.text_ypos = self.text_ypos + self.scroll_speed
        self.surface.fill(self.text_bgcolor, (0,0,self.title_surface.get_width(),self.height))
        self.surface.blit(self.title_surface, (self.text_xpos,self.text_ypos))
        self.surface.blit(self.graph_surface, (self.width - self.graph_surface.get_width(),0))

