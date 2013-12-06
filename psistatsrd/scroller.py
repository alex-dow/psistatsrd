import pygame
import math
class Scroller(object):

    def __init__(self, *args, **kwargs):
        self.bgcolor      = kwargs["bgcolor"] if "bgcolor" in kwargs else (30,30,30)
        self.color        = kwargs["color"] if "color" in kwargs else (255,255,255)
        self.width        = kwargs['width'] if 'width' in kwargs else 50
        self.height       = kwargs['height'] if 'height' in kwargs else 20
        self.scroll_speed = kwargs['scroll_speed'] if 'scroll_speed' in kwargs else 1
        self.scroll_pause = kwargs['scroll_pause'] if 'scroll_pause' in kwargs else 20
        self.scroll_delay = kwargs['scroll_delay'] if 'scroll_delay' in kwargs else 25
        self.text_font   = kwargs['text_font'] if 'text_font' in kwargs else "monospace"
        self.text_size   = kwargs['text_size'] if 'text_size' in kwargs else 8
        self.text_aa     = kwargs['text_aa'] if 'text_aa' in kwargs else True
        self.idx    = 0
        self.list_len    = 0
        self.current_text = ""
        self.text_lines = kwargs['text_lines'] if 'text_lines' in kwargs else []
        self.text_ypos = 0
        self.text_xpos = 0
       
        if isinstance(self.text_lines, list):
            self.current_text = self.text_lines[self.idx]
            self.list_len = len(self.text_lines)

        self.text_xpos   = 0
        self.text_ypos   = self.height - self.scroll_delay
        self.text_pause  = 0

        self.scroll_pos = 1

        self.surface = pygame.Surface((self.width, self.height))

        try:
            with open('%s.ttf' % self.text_font):
                self.font = pygame.font.Font('%s.ttf' % self.text_font, self.text_size)
        except IOError:
            self.font = pygame.font.SysFont(self.text_font, self.text_size)

        self.text_surface = self.font.render(self.current_text, self.text_aa, self.color, self.bgcolor)

        self.ypos_mid = math.ceil(self.height / 2)

    def draw(self):
        if self.text_ypos >= self.ypos_mid and self.scroll_pos == 1:
            if self.text_pause < self.scroll_pause:
                self.text_pause = self.text_pause + 1
            else:
                self.text_pause = 0
                self.scroll_pos = 2
                self.text_ypos = self.text_ypos + self.scroll_speed
        else:
            if self.text_ypos > (self.height + self.scroll_delay):
                self.text_ypos = -self.scroll_delay + -self.height
                self.scroll_pos = 1
                if self.list_len > 0:
                    self.idx = self.idx + 1
                    if self.idx == self.list_len:
                        self.idx = 0
                    self.current_text = self.text_lines[self.idx]
                
                self.text_surface = self.font.render(self.current_text, self.text_aa, self.color)
            
            self.text_ypos = self.text_ypos + self.scroll_speed

        self.surface.fill(self.bgcolor)
        self.surface.blit(self.text_surface, (self.text_xpos,self.text_ypos))
 
