#!/usr/bin/env python
import pygame
import traceback
import sys
import numpy as np
from pygame.locals import *
import random
import math
from psistatsrd.graph import Graph
from psistatsrd.graph2 import Graph2
from psistatsrd import args
from psistatsrd.config import Config
import json
from psistatsrd import subscriber
import logging
import logging.config
from count_chars import count_chars
from psistatsrd.scroller import Scroller
from psistatsrd.statrow import StatRow
import requests

POLL_EVENT = pygame.USEREVENT + 1
DRAW_EVENT = pygame.USEREVENT + 2
BIND_EVENT = pygame.USEREVENT + 3

pygame.init()

FLAGS = 0

c = Config(args.args['config_file'])
c.parse()

logging.config.fileConfig(args.args['config_log_file'])

if c.params['display.fullscreen'] == True:
    FLAGS = FLAGS | FULLSCREEN

if c.params['display.doublebuf'] == True:
    FLAGS = FLAGS | DOUBLEBUF

window = pygame.display.set_mode((int(c.params['display.width']), int(c.params['display.height'])), FLAGS)
screen = pygame.display.get_surface()
screen.fill(c.params['display.bgcolor'])

pygame.mouse.set_visible(False)

clock = pygame.time.Clock()

numbers = [0]

DRAW_INTERVAL = int(c.params['draw_interval'])
POLL_INTERVAL = int(c.params['poll_interval'])
BIND_INTERVAL = int(c.params['bind_interval'])
FPS           = int(c.params['fps'])
TIMER         = int(float(1000) * (float(1) / float(FPS)))

logging.debug("Timers:")
logging.debug("Draw Timer: %d" % DRAW_INTERVAL)
logging.debug("Poll Timer: %d" % POLL_INTERVAL)
logging.debug("Bind Timer: %d" % BIND_INTERVAL)
logging.debug("FPS       : %d" % FPS)

logging.debug("Timer     : %f" % TIMER)

pygame.time.set_timer(USEREVENT+1, POLL_INTERVAL)
# pygame.time.set_timer(USEREVENT+2, DRAW_INTERVAL)
pygame.time.set_timer(USEREVENT+3, BIND_INTERVAL)

cpu_graphs = {}
mem_graphs = {}
scrollers = {}

rows = {}

computers = []
queues = []
misses = {}
status_received = []

no_computers_surface = False
RUN = True

class Screen(object):
    
    def __init__(self, id, config):
        self.id = id
        self.config = config

    @property
    def background_color(self):

        if "screen.%s.background_color" % self.id in self.config:
            try:
                colors = self.config.split(",",3)
                if len(colors) < 3:
                    raise TypeError()
            except:
                logging.error("ERROR - Background color for screen %s invalid format" % self.id)
        else:
            return (0,0,0)

def msg_callback(ch, method, properties, body):
    try:
        body = body.replace('\x00','')
        logging.debug(body.replace('\n',' '))
        obj = json.loads(body, encoding='utf-8')
        queuename = "psistats-%s" % obj['hostname']
        title = []

        if type(obj['ipaddr']).__name__ == "list":
            title = title + obj['ipaddr']
        else:
            title = [obj['ipaddr']]

        if obj['hostname'] not in computers:
            computers.append(obj['hostname'])

            if queuename not in queues:
                queues.append(queuename)

            if queuename not in mem_graphs:
                mem_graphs[queuename] = Graph2(
                    height = int(c.params['graph.mem.height']),
                    width = int(c.params['graph.mem.width']),
                    line_width = int(c.params['graph.mem.line_width']),
                    color = c.params['graph.mem.color'],
                    bgcolor = c.params['graph.mem.bgcolor'],
                    line_aa = c.params['graph.mem.line_aa']
                )
                if 'graph.mem.max_color' in c.params:
                    mem_graphs[queuename].max_color = c.params['graph.mem.max_color']

                 
                if 'graph.mem.min_color' in c.params:
                    mem_graphs[queuename].min_color = c.params['graph.mem.min_color']

            if queuename not in cpu_graphs:
                cpu_graphs[queuename] = Graph2(
                    height = int(c.params['graph.cpu.height']),
                    width = int(c.params['graph.cpu.width']),
                    line_width = int(c.params['graph.cpu.line_width']),
                    color = c.params['graph.cpu.color'],
                    bgcolor = c.params['graph.cpu.bgcolor'],
                    line_aa = c.params['graph.cpu.line_aa']
                )

                if 'graph.cpu.max_color' in c.params:
                    cpu_graphs[queuename].max_color = c.params['graph.cpu.max_color']
                if 'graph.cpu.min_color' in c.params:
                    cpu_graphs[queuename].min_color = c.params['graph.cpu.min_color']

            if queuename not in scrollers:
                scrollers[queuename] = Scroller(
                    scroll_speed = float(c.params['scroller.scroll_speed']),
                    scroll_delay = int(c.params['scroller.scroll_delay']),
                    scroll_pause = int(c.params['scroller.scroll_pause']),
                    text_font = c.params['scroller.font.name'],
                    text_aa = c.params['scroller.font.aa'],
                    text_size = int(c.params['scroller.font.size']),
                    width = int(c.params['scroller.width']),
                    height = int(c.params['scroller.height']),
                    color=c.params['scroller.color'],
                    bgcolor=c.params['scroller.bgcolor'],
                    text_lines=title
                )
            if queuename not in rows:
                rows[queuename] = StatRow(
                    border_width=int(c.params['statrow.border_width']),
                    border_color=c.params['statrow.border_color'],
                    height=int(c.params['statrow.height']),
                    width=int(c.params['statrow.width']),
                    bgcolor=c.params['statrow.bgcolor'],
                    title_font_size=int(c.params['statrow.title_font_size']),
                    title_font_aa=c.params['statrow.title_font_aa'],
                    title_font=c.params['statrow.title_font'],
                    title_color=c.params['statrow.title_color'],
                    host=obj['hostname']
                )
                rows[queuename].add_drawable(scrollers[queuename])
                rows[queuename].add_drawable(cpu_graphs[queuename])
                rows[queuename].add_drawable(mem_graphs[queuename])

       
        rows[queuename].draw("%s - %s" % (obj['hostname'], obj['uptime']))
            
        cpu_graphs[queuename].process(obj['cpu'] / 100)
        mem_percent = float(obj['mem_used']) / float(obj['mem_total'])
    
        mem_graphs[queuename].process(mem_percent)
        status_received.append(queuename)
        misses[queuename] = 0
        
    except:
        logging.error(sys.exc_info()[0])
        logging.error(sys.exc_info()[1])
        traceback.print_tb(sys.exc_info()[2])


error_count = int(c.params['tweaks.error_threshold'])
ERROR_MODE = True

while RUN:
    
    for event in pygame.event.get():
        if event.type == POLL_EVENT:

            if error_count >= int(c.params['tweaks.error_threshold']):
                ERROR_MODE = True
                logging.error("--- ERROR MODE - ERR COUNT %i ---", error_count)
                if error_count >= (int(c.params['tweaks.error_threshold']) * 5):
                    logging.critical('--- HEY I THINK SOMETHING IS WRONG HERE!!!! ---')
                try:
                    connection = subscriber.get_connection(c.params)
                    channel = subscriber.setup_channel(c.params, connection)
                    error_count = 0
                    ERROR_MODE = False
                    screen.fill(c.params['display.bgcolor'])
                except:
                    logging.critical('--- ERROR MODE ERROR ---')
                    logging.exception(sys.exc_info()[1])
                    error_count = error_count + 1
                    continue
                
                    

            try:
                subscriber.get_messages(msg_callback, c.params, channel)
                for queue in queues:
                    if (queue not in status_received):
                        misses[queue] += 1
                    else:
                        misses[queue] = 0

                    if misses[queue] == 0:
                        rows[queue].do_draw = True
                        rows[queue].title_color = c.params['statrow.title_color']
                        
                    elif misses[queue] > int(c.params['tweaks.remove_misses']):

                        i = queues.index(queue)
                        position = i * (rows[queue].surface.get_height() + int(c.params['statrow.padding']))
                        screen.fill(c.params['display.bgcolor'], (0,position,rows[queue].surface.get_width(), rows[queue].surface.get_height()))

                        del rows[queue]
                        del cpu_graphs[queue]
                        del misses[queue]
                        del mem_graphs[queue]
                        del scrollers[queue]
                        i = queues.index(queue)
                        del queues[i]
                        screen.fill(c.params['display.bgcolor'])
                        
                    elif misses[queue] > int(c.params['tweaks.offline_misses']):
                        rows[queue].title = "%s - OFFLINE!" % rows[queue].host
                        rows[queue].update_title()
                        rows[queue].do_draw = False
                    elif misses[queue] > int(c.params['tweaks.error_misses']):
                        rows[queue].title_color = (255,0,0)
                        rows[queue].update_title()
                        rows[queue].do_draw = False
                    elif misses[queue] > int(c.params['tweaks.warning_misses']):
                        rows[queue].title_color = (255,255,0)
                        rows[queue].update_title()

                status_received = []
            except:
                logging.exception(sys.exc_info()[1])
                error_count = error_count + 1
        elif event.type == DRAW_EVENT:
            if ERROR_MODE == True:
                err_surface = pygame.image.load("error.png")
                screen.blit(err_surface, (0, 0))
            else:
                height = 0
                for queuename in queues:
                    row = rows[queuename]
                    row.draw()
                    screen.blit(row.surface, (0, height))
                    height = height + row.surface.get_height() + int(c.params['statrow.padding'])
            pygame.display.flip()

        elif event.type == BIND_EVENT:
            logging.debug("Binding queues")
            try:
                subscriber.bind_queues(c.params)
            except requests.exceptions.ConnectionError as e:
                logging.critical("Could not bind queues because I could not connect to RabbitMQ API: %s" % e.message)
                error_count = error_count + 1
                
        elif event.type == pygame.QUIT:
            RUN = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                RUN = False
        
    if ERROR_MODE == True:
        err_surface = pygame.image.load("error.png")
        screen.blit(err_surface, (0, 0))
    else:
        height = 0
        for queuename in queues:
            row = rows[queuename]
            row.draw()
            screen.blit(row.surface, (0, height))
            height = height + row.surface.get_height() + int(c.params['statrow.padding'])
    pygame.display.flip()
     
#    pygame.display.flip()
    pygame.time.wait(TIMER)



