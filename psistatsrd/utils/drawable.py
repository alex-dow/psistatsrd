import pygame
import sys
from psistatsrd.app import App


def create_queue_row(data, config):
    mem_graph = create_mem_graph(config)
    cpu_graph = create_cpu_graph(config)

    scroll_text = []

    title = []

    if type(data['ipaddr']).__name__ == "list":
        scroll_text = scroll_text + data['ipaddr']
    else:
        scroll_text = [data['ipaddr']]

    scroller = create_scroller(scroll_text, config)
    row = create_row(config)

    row.add_drawable('scroller', scroller, App.DRAW_EVENT)
    row.add_drawable('cpu', cpu_graph, App.POLL_EVENT)
    row.add_drawable('mem', mem_graph, App.POLL_EVENT)

    return row

def create_row(config):
    row = StatRow(
        border_width=int(config['statrow.border_width']),
        border_color=config['statrow.border_color'],
        height=int(config['statrow.height']),
        width=int(config['statrow.width']),
        bgcolor=config['statrow.bgcolor'],
        title_font_size=int(config['statrow.title_font_size']),
        title_font_aa=config['statrow.title_font_aa'],
        title_font=config['statrow.title_font'],
        title_color=config['statrow.title_color'],
    )
    return row


def create_scroller(scroll_text, config):
    s = Scroller(
        scroll_speed = float(config['scroller.scroll_speed']),
        scroll_delay = int(config['scroller.scroll_delay']),
        scroll_pause = int(config['scroller.scroll_pause']),
        text_font = config['scroller.font.name'],
        text_aa = config['scroller.font.aa'],
        text_size = int(config['scroller.font.size']),
        width = int(config['scroller.width']),
        height = int(config['scroller.height']),
        color=config['scroller.color'],
        bgcolor=config['scroller.bgcolor'],
        text_lines=scroll_text
    )
    return s
       

def create_resource_graph(key, config):
    g = Graph2(
        height=int(config['graph.%s.height' % key]),
        width=int(config['graph.%s.width' % key]),
        line_width=int(config['graph.%s.line_width' % key]),
        color=config['graph.%s.color' % key],
        bgcolor=config['graph.%s.bgcolor' % key],
        line_aa=config['graph.%s.line_aa' % key]
    )

    max_color = 'graph.%s.max_color' % key
    min_color = 'graph.%s.min_color' % key

    if max_color in config:
        g.max_color = config[max_color]

    if min_color in config:
        g.min_color = config[min_color]

    return g


def create_cpu_graph(config):
    return create_resource_graph('cpu', config)

def create_mem_graph(config):
    return create_resource_graph('mem', config)
       

from psistatsrd.app import App
from psistatsrd.graph2 import Graph2
from psistatsrd.scroller import Scroller
from psistatsrd.statrow import StatRow


