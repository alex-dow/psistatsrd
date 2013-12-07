import pygame
import pygame.event
from pygame.locals import DOUBLEBUF, FULLSCREEN
import sys
from utils import rabbitmq

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
        self.error_count = self.error_count + 1
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
    def __init__(self, warning_threshold, error_threshold, offline_threshold, remove_threshold):
        self.queue_rows = {}
        self.processed_rows = []
        self.missed_queues = {}
        self.error_queues = []
        self.warning_queues = []
        self.offline_queues = []
        self.remove_queues = []
        self.warning_threshold = warning_threshold
        self.error_threshold = error_threshold
        self.offline_threshold = offline_threshold
        self.remove_threshold = remove_threshold
        

    def add_queue_row(self, queue, queue_row):
        self.queue_rows[queue] = queue_row

    def has_queue_row(self, queue):
        return (queue in self.queue_rows)

    def get_queue_row(self, queue):
        if queue in self.queue_rows:
            return self.queue_rows[queue]
        else:
            return None

    def add_processed(self, queue):
        if queue not in self.processed_rows:
           self.processed_rows.append(queue)
   
    def reset_processed(self):
        self.processed_rows = []

    def reset_misses(self, queue):
        if queue in self.missed_queues:
            del self.missed_queues[queue]

        if queue in self.warning_queues:
            self.warning_queues.remove(queue)

        if queue in self.error_queues:
            self.error_queues.remove(queue)

        if queue in self.offline_queues:
            self.offline_queues.remove(queue)

        if queue in self.remove_queues:
            self.remove_queues.remove(queue)

    def get_misses(self):
        keys = self.queue_rows.keys()
        for missed in list(set(keys) - set(self.processed_rows)):
            if missed not in self.missed_queues:
                self.missed_queues[missed] = 1
            else:
                self.missed_queues[missed] = self.missed_queues[missed] + 1

            if self.missed_queues[missed] >= self.remove_threshold:
                if missed not in self.remove_queues:
                    self.remove_queues.append(missed)
                    self.offline_queues.remove(missed)
            elif self.missed_queues[missed] >= self.offline_threshold:
                if missed not in self.offline_queues:
                    self.offline_queues.append(missed)
                    self.error_queues.remove(missed)
                continue
            elif self.missed_queues[missed] >= self.error_threshold:
                if missed not in self.error_queues:
                    self.error_queues.append(missed)
                    self.warning_queues.remove(missed)
                continue
                
            elif self.missed_queues[missed] >= self.warning_threshold and missed not in self.warning_queues:
                self.warning_queues.append(missed)

        return self.missed_queues
         

class App(object):

    DRAW_EVENT = pygame.USEREVENT
    POLL_EVENT = pygame.USEREVENT+1
    OFFLINE_EVENT = pygame.USEREVENT+2
    BIND_EVENT = pygame.USEREVENT+3

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
        pygame.time.set_timer(App.OFFLINE_EVENT, int(config['offline_interval']))
        pygame.time.set_timer(App.BIND_EVENT, int(config['bind_interval']))

        status = Status()
   
        queue_rows = QueueRows(
            warning_threshold=int(config['tweaks.warning_threshold']),
            error_threshold=int(config['tweaks.error_threshold']),
            offline_threshold=int(config['tweaks.offline_threshold']),
            remove_threshold=int(config['tweaks.remove_threshold'])
        )   

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
                        for qn, qr in queue_rows.queue_rows.iteritems():
                            if qn in queue_rows.processed_rows:
                                queue_rows.reset_misses(qn)
                                qr.title_color = config['statrow.title_color']
                            qr.draw(App.POLL_EVENT)
                        queue_rows.reset_processed()
                    elif event.type == App.BIND_EVENT:
                        rabbitmq.bind_queues(config)
                    elif event.type == App.OFFLINE_EVENT:
                        queue_rows.get_misses()

                        if len(queue_rows.remove_queues) > 0:
                            for queue in queue_rows.remove_queues:
                                del queue_rows.queue_rows[queue]
                                queue_rows.reset_misses(queue)
                            screen.fill(config['display.bgcolor'])
                        if len(queue_rows.offline_queues) > 0:
                            for queue in queue_rows.offline_queues:
                                self._logger.critical("Queue is offline! %s", queue)
                                queue_rows.queue_rows[queue].title_color = config['statrow.title_error_color']
                                queue_rows.queue_rows[queue].update_title("%s - OFFLINE!" % queue_rows.queue_rows[queue].host)
                        if len(queue_rows.error_queues) > 0:
                            for queue in queue_rows.error_queues:
                                self._logger.error("Queue is error! %s", queue)
                                queue_rows.queue_rows[queue].title_color = config['statrow.title_error_color']
                                queue_rows.queue_rows[queue].update_title(queue_rows.queue_rows[queue].title)
                        if len(queue_rows.warning_queues) > 0:
                            for queue in queue_rows.warning_queues:
                                queue_rows.queue_rows[queue].title_color = config['statrow.title_warning_color']
                                queue_rows.queue_rows[queue].update_title(queue_rows.queue_rows[queue].title)
                                self._logger.warning("Queue is warning! %s", queue) 

                height = 0

                for qn, qr in queue_rows.queue_rows.iteritems():
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

