import pygame
import math

class StatRow(object):
    
    def __init__(self, *args, **kwargs):
        
        self.host  = kwargs['host'] if 'host' in kwargs else None        
        self.height = kwargs['height'] if 'height' in kwargs else 20
        self.width = kwargs['width'] if 'width' in kwargs else 100
        self.bgcolor = kwargs['bgcolor'] if 'bgcolor' in kwargs else (0,0,0)
        self.title = kwargs['title'] if 'title' in kwargs else None
        self.title_color = kwargs['title_color'] if 'title_color' in kwargs else (255,255,255)
        self.title_font_size = kwargs['title_font_size'] if 'title_font_size' in kwargs else 11
        self.title_font = kwargs['title_font'] if 'title_font' in kwargs else 'monospace'
        self.title_font_aa = kwargs['title_font_aa'] if 'title_font_aa' in kwargs else False
        self.title_bgcolor = kwargs['title_bgcolor'] if 'title_bgcolor' in kwargs else self.bgcolor
        self.border_width = kwargs['border_width'] if 'border_width' in kwargs else 0
        self.border_color = kwargs['border_color'] if 'border_color' in kwargs else (0,0,0)
        self.spacing = kwargs['spacing'] if 'spacing' in kwargs else 0


        self.maximum_width = 0
        self.x_positions = {}
        self.drawables = {}
        self.events = {}
        self.do_draw = True

 
        try:
            with open('%s.ttf' % self.title_font):
                self.font = pygame.font.Font('%s.ttf' % self.title_font, self.title_font_size)
        except IOError:
            self.font = pygame.font.SysFont(self.title_font, self.title_font_size)

        self.text_surface = self.font.render(self.title, self.title_font_aa, self.title_color, self.bgcolor)
        
        self.title_offset = self.text_surface.get_height()
        self._height = self.height + self.text_surface.get_height()

        self.surface = pygame.Surface((self.width, self._height))
        self.surface.fill(self.bgcolor)
 
    def update_title(self, title):
        self.text_surface = self.font.render(self.title, self.title_font_aa, self.title_color, self.title_bgcolor)
        self.title = title
        
    
    def add_drawable(self, name, drawable, event):
        if event not in self.events:
            self.events[event] = []

        self.events[event].append(name)
        self.drawables[name] = drawable
        self.x_positions[name] = self.maximum_width
        self.maximum_width = self.maximum_width + drawable.surface.get_width()

    def get_drawable(self, name):
        if name in self.drawables:
            return self.drawables[name]
        else:
            return None

    def get_drawable_event(self, name):
        if name in self.events:
            return self.events.index(name)


    def draw(self, event, title=None):
        if title != None:
            self.update_title(title)
        
        if self.border_width > 0:
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
            for d_id in self.events[event]:
                if d_id in self.drawables:
                    d = self.drawables[d_id]
                    x_offset = self.x_positions[d_id]
                    d.draw()
                    self.surface.blit(d.surface, (x_offset, self.title_offset))
                else:
                    raise AttributeError("%s drawable id not found in list of drawables!")

        self.surface.blit(self.text_surface,(0,0))
        if self.border_width > 0:
            borders = [
                (0,0),
                (self.width-self.border_width,0),
                (self.width-self.border_width,self._height-self.border_width),
                (0,self._height-self.border_width),
                (0,0)
            ]
            pygame.draw.lines(self.surface, self.border_color, False, borders, self.border_width)
       
          

