import sys
import time
import threading
import pygame
import simplejson as json
from utils import rabbitmq
from utils import drawable

class WorkerThread(threading.Thread):

    def __init__(self, logger, status, conf, queue_rows):
        threading.Thread.__init__(self)
        self._error_count = 0
        self._logger = logger
        self._status = status
        self._queue_rows = queue_rows

        self.config = conf
        self.running = True
        

    def process_msg(self, body):
        body = body.replace('\x00','')
        self._logger.debug(body.replace('\n',' '))
        
        obj = json.loads(body, encoding='utf-8')
        return obj   
 
    def run(self):

        connection = None
        channel = None

        ack_rate = int(self.config['tweaks.ack_rate'])
        ack_delay = int(self.config['tweaks.ack_delay'])

        while self.running == True:
            if connection == None or channel == None:
                try:
                    self._logger.debug('Create connection')
                    connection = rabbitmq.get_connection(self.config)
                    
                    self._logger.debug('Create channel')
                    channel = rabbitmq.setup_channel(self.config, connection)

                    if self._status.isError():
                        self._status.nowNormal()
                except:
                    self._logger.error('Error trying to connect to RabbitMQ')
                    self._logger.exception(sys.exc_info()[1])
                    self._status.error()
                    
                    connection = None
                    channel = None
                    pygame.time.wait(1000)
                    continue
            else:
                try:
                    if self._status.isError():
                        self._logger.debug("Error mode active, disabling connection")
                        connection = None
                        channel = None
                    else:
                        total_msgs = 0
                        for method_frame, properties, body in channel.consume(self.config['amqp.queue']):
                            self._logger.debug("msg recv: %s" % body)
                            pygame.time.wait(ack_delay)
                            total_msgs += 1
                            if total_msgs > ack_rate:
                                break

                            data = self.process_msg(body)

                            queue_name = "psistats-%s" % data['hostname']

                            if self._queue_rows.has_queue_row(queue_name) == False:
                                qr = drawable.create_queue_row(data, self.config)
                                self._queue_rows.add_queue_row(queue_name, qr)

                            if self._queue_rows.has_queue_row(queue_name):
                                qr = self._queue_rows.get_queue_row(queue_name)
                                qr.get_drawable('cpu').process(float(data['cpu']) / float(100))
                                
                                qr.get_drawable('mem').process(float(data['mem_used']) / float(data['mem_total']))
                                qr.update_title("%s - %s" % (data['hostname'], data['uptime']))
                            
                        channel.cancel()
                    pygame.time.wait(1000)
                except:
                    self._logger.error('Error trying to fetch messages')
                    self._logger.exception(sys.exc_info()[1])
                    self._status.error()
        self._logger.warning("Worker thread exiting!")

