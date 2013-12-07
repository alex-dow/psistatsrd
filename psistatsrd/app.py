import pygame
import pygame.event
from pygame.locals import DOUBLEBUF, FULLSCREEN
import sys

class StopLoop(Exception):
    def __str__(self):
        return 'StopLoop'

class Status(object):
    NORMAL = 0
    ERROR = 1

    def __init__(self, threshold=10):
        self.status = 0
        self.error_count = 0
        self.threshold = threshold

    def normal(self):
        self.status = Status.NORMAL
    
    def error(self):
        self.error_count + self.error_count + 1
        if (self.error_count > self.threshold):
            self.status = Status.ERROR

    def isError(self):
        return self.status == Status.ERROR

    def isNormal(self):
        return self.status == Status.NORMAL

    def nowNormal(self):
        self.status = Status.NORMAL
        self.error_count = 0

class QueueRows(object):
    def __init__(self):
        self.queue_rows = {}

    def add_queue_row(self, queue, queue_row):
        self.queue_rows[queue] = queue_row

    def has_queue_row(self, queue):
        return (queue in self.queue_rows)

    def get_queue_row(self, queue):
        if queue in self.queue_rows:
            return self.queue_rows[queue]
        else:
            return None


class App(object):

    DRAW_EVENT = pygame.USEREVENT
    POLL_EVENT = pygame.USEREVENT+1

    def __init__(self, config, logger):
        self.config = config
        self.running = True
        self._logger = logger


    def run(self):
        config = self.config
        self._logger.info("Starting Application")
        self._logger.debug("Initializing pygame")
        pygame.init()
        pygame.mouse.set_visible(False)

        FLAGS = 0
        if self.config['display.fullscreen'] == True:
            FLAGS = FLAGS | FULLSCREEN

        if self.config['display.doublebuf'] == True:
            FLAGS = FLAGS | DOUBLEBUF
        self._logger.debug("Creating screen")
        window = pygame.display.set_mode((int(config['display.width']), int(config['display.height'])), FLAGS)
        screen = pygame.display.get_surface()
        screen.fill(config['display.bgcolor'])

        self._logger.debug("Creating timers")
        pygame.time.set_timer(App.POLL_EVENT, int(config['poll_interval']))

        status = Status()
        queue_rows = QueueRows()

        self._logger.debug("Creating Worker Thread")
        worker_thread = worker.WorkerThread(
            logger=self._logger, 
            status=status, 
            conf=self.config,
            queue_rows=queue_rows
        )
        
        self._logger.debug("Starting Worker Thread")
        worker_thread.start()

        main_loop_timer = int(float(1000) * (float(1) / float(self.config['fps'])))
        self._logger.debug("Main loop timer: %d milliseconds" % main_loop_timer)


        while self.running:
            try:
                POLL_DRAW = False
                for event in pygame.event.get():
                    if event.type == App.POLL_EVENT:
                        POLL_DRAW = True

                height = 0
                for k, qr in queue_rows.queue_rows.iteritems():
                    if (POLL_DRAW == True):
                        qr.draw(App.POLL_EVENT)
                    qr.draw(App.DRAW_EVENT)
                    screen.blit(qr.surface, (0, height))
                    height = height + qr.surface.get_height() + int(config['statrow.padding'])

                pygame.display.flip()
                pygame.time.wait(main_loop_timer)
            except KeyboardInterrupt, StopLoop:
                self.running = False
                worker_thread.running = False
            except:
                self._logger.error("Error in main loop")
                self._logger.exception(sys.exc_info()[1])
                status.error()
        self._logger.warn("Leaving application")

import worker

