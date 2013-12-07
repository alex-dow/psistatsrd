#!/usr/bin/env python
import sys
import os
import inspect


cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    print "adding %s to sys path" % cmd_folder
    sys.path.insert(1, cmd_folder)

# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"psistatsrd")))
#if cmd_subfolder not in sys.path:
#    print "adding %s to sys path" % cmd_subfolder
#    sys.path.insert(1, cmd_subfolder)




import logging
import logging.config
import pygame
from pygame.locals import FULLSCREEN, DOUBLEBUF
from psistatsrd.app import App
import psistatsrd.args
import psistatsrd.config
from psistatsrd.utils import rabbitmq


config_file = psistatsrd.args.args['config_file']
config_log_file = psistatsrd.args.args['config_log_file']
logging.config.fileConfig(config_log_file)

logging.debug("Loading configuration file")
c = psistatsrd.config.Config(config_file)
c.parse()

config = c.params

PYGAME_FLAGS = 0
 
if config['display.fullscreen'] == True:
    PYGAME_FLAGS = PYGAME_FLAGS | FULLSCREEN

if config['display.doublebuf'] == True:
    PYGAME_FLAGS = PYGAME_FLAGS | DOUBLEBUF


logging.info("Bind queues")
# rabbitmq.bind_queues(config)
logging.info("App.run()")
app = App(config=config, logger=logging)
app.run()

