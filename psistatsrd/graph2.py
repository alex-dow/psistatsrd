import pygame
import random
import math

class Graph2(object):

    SCROLL_TOP = 1
    SCROLL_BOTTOM = 2

    def __init__(self, *args, **kwargs):
        self.bgcolor      = kwargs["bgcolor"] if "bgcolor" in kwargs else (30,30,30)
        self.color        = kwargs["color"] if "color" in kwargs else (255,255,255)
        self.line_width   = kwargs['line_width'] if 'line_width' in kwargs else 1
        self.line_aa      = kwargs['line_aa'] if 'line_aa' in kwargs else False
        self.width        = kwargs['width'] if 'width' in kwargs else 50
        self.height       = kwargs['height'] if 'height' in kwargs else 20
        self.max_color    = kwargs['max_color'] if 'max_color' in kwargs else None
        self.min_color    = kwargs['min_color'] if 'min_color' in kwargs else None

        if (self.max_color != None and type(self.max_color).__name__ != "Color"):
            self.max_color = pygame.Color(self.max_color)
        if (self.min_color != None and type(self.min_color).__name__ != "Color"):
            self.min_color = pygame.Color(self.min_color)
        if (self.color != None and type(self.color).__name__ != "Color"):
            self.color = pygame.Color(self.color)

        self.numbers = [0]

        self.surface = pygame.Surface((self.width, self.height))


    def process(self, number):
        self.numbers.append(number)
        if (len(self.numbers) == self.surface.get_width()):
            self.numbers = self.numbers[1:]

    def draw(self):
        if len(self.numbers) == 0:
            return

        self.surface.fill(self.bgcolor)

        for idx, h in enumerate(self.numbers):

            if (self.max_color != None and self.min_color != None):
                line_color = pygame.Color("black")
                if (self.max_color.r > self.min_color.r):
                    line_color.r = int(round(h * math.fabs(self.max_color.r - self.min_color.r)))
                else:
                    line_color.r = (self.min_color.r - self.max_color.r) - int(round(h * math.fabs(self.min_color.r - self.max_color.r)))

                if (self.max_color.g > self.min_color.g):
                    line_color.g = int(round(h * math.fabs(self.max_color.g - self.min_color.g)))
                else:
                    line_color.g = (self.min_color.g - self.max_color.g) - int(round(h * math.fabs(self.min_color.g - self.max_color.g)))

                if (self.max_color.b > self.min_color.b):
                    line_color.b = int(round(h * math.fabs(self.max_color.b - self.min_color.b)))
                else:
                    line_color.b = (self.min_color.b - self.max_color.b) - int(round(h * math.fabs(self.min_color.b - self.max_color.b)))
                
            else:
                line_color = self.color
                

            pygame.draw.line(self.surface, line_color, 
                (idx, self.surface.get_height()), 
                (idx, (self.surface.get_height() - (h * self.surface.get_height())))
            )
        

