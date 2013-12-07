import pika
import requests
import time
import simplejson as json
from requests.auth import HTTPBasicAuth

def get_admin_url(conf, command):
    return 'http://%s:%d/api/%s' % (conf['amqp.host'], int(conf['amqp.admin_port']), command)

def get_queues(conf):
    url = get_admin_url(conf, 'queues')
    r = requests.get(url, auth=HTTPBasicAuth(conf['amqp.username'], conf['amqp.password']))
    return json.loads(r.text)

def get_connection(conf):
    rmq_cred = pika.PlainCredentials(conf['amqp.username'], conf['amqp.password'])
    rmq_params = pika.ConnectionParameters(
        conf['amqp.host'],
        int(conf['amqp.port']),
        conf['amqp.vhost'],
        rmq_cred
    )

    return pika.BlockingConnection(parameters=rmq_params)

def setup_channel(conf, connection):
    channel = connection.channel()
    channel.exchange_declare(
        exchange=conf['amqp.exchange'],
        type=conf['amqp.exchange_type'],
        durable=conf['amqp.exchange_durable'],
        auto_delete=conf['amqp.exchange_autodelete']
    )

    channel.queue_declare(
        queue=conf['amqp.queue'],
        exclusive=conf['amqp.queue_exclusive'],
        durable=conf['amqp.queue_durable'],
        auto_delete=conf['amqp.queue_autodelete'],
        arguments={
            "x-message-ttl": int(conf['amqp.queue_ttl'])
        }
    )
    return channel

def bind_queues(conf):
    queues = get_queues(conf) 
    connection = get_connection(conf)
    channel = setup_channel(conf, connection) 

    for q in queues:
        channel.queue_bind(
            queue=conf['amqp.queue'],
            exchange=conf['amqp.exchange'],
            routing_key=str(q['name'])
        )
    connection.close()
        
