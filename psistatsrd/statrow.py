import pygame
import math

class StatRow(object):
    
    def __init__(self, *args, **kwargs):
        
        self.host  = kwargs['host'] if 'host' in kwargs else None        
        self.height = kwargs['height'] if 'height' in kwargs else 20
        self.width = kwargs['width'] if 'width' in kwargs else 100
        self.bgcolor = kwargs['bgcolor'] if 'bgcolor' in kwargs else (0,0,0)
        self.title = kwargs['title'] if 'title' in kwargs else 'Undefined Title'
        self.title_color = kwargs['title_color'] if 'title_color' in kwargs else (255,255,255)
        self.title_font_size = kwargs['title_font_size'] if 'title_font_size' in kwargs else 11
        self.title_font = kwargs['title_font'] if 'title_font' in kwargs else 'monospace'
        self.title_font_aa = kwargs['title_font_aa'] if 'title_font_aa' in kwargs else False
        self.title_bgcolor = kwargs['title_bgcolor'] if 'title_bgcolor' in kwargs else self.bgcolor
        self.border_width = kwargs['border_width'] if 'border_width' in kwargs else 0
        self.border_color = kwargs['border_color'] if 'border_color' in kwargs else (0,0,0)
        self.spacing = kwargs['spacing'] if 'spacing' in kwargs else 0

        self.drawables = []
        self.do_draw = True

        self.surface = pygame.Surface((self.width, self.height))
 
        try:
            with open('%s.ttf' % self.title_font):
                self.font = pygame.font.Font('%s.ttf' % self.title_font, self.title_font_size)
        except IOError:
            self.font = pygame.font.SysFont(self.title_font, self.title_font_size)

        self.text_surface = self.font.render(self.title, self.title_font_aa, self.title_color, self.bgcolor)
        
        self.title_offset = self.text_surface.get_height()
        self._height = self.height + self.text_surface.get_height()

        self.surface = pygame.Surface((self.width, self._height))

    def update_title(self):
        self.text_surface = self.font.render(self.title, self.title_font_aa, self.title_color, self.title_bgcolor)
        
    
    def add_drawable(self, drawable):
        self.drawables.append(drawable)

    def draw(self, title=None):
        if title != None:
            self.title = title
            self.update_title()
        self.surface.fill(self.bgcolor)
        
        if self.border_width == 0:
            borders = [
                (0,0),
                (self.width-self.border_width,0),
                (self.width-self.border_width,self._height-self.border_width),
                (0,self._height-self.border_width),
                (0,0)
            ]
        pygame.draw.lines(self.surface, self.border_color, False, borders, self.border_width)

        x_offset = 0
        
        if self.do_draw == True:
            for d in self.drawables:
                d.draw()
                self.surface.blit(d.surface, (x_offset, self.title_offset))
                x_offset = x_offset + d.surface.get_width()

        self.surface.blit(self.text_surface,(0,0))
        
        if self.border_width == 0:
            pygame.draw.lines(self.surface, self.border_color, False, borders, self.border_width)
            
            
        


