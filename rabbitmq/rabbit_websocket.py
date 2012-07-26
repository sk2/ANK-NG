# based on http://reminiscential.wordpress.com/2012/04/07/realtime-notification-delivery-using-rabbitmq-tornado-and-websocket/
import pika
import tornado
import tornado.websocket as websocket
from pika.adapters.tornado_connection import TornadoConnection

class MyWebSocketHandler(websocket.WebSocketHandler):
    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self, *args, **kwargs):
        self.application.pc.add_event_listener(self)
        pika.log.info("WebSocket opened")

    def on_close(self):
        pika.log.info("WebSocket closed")
        self.application.pc.remove_event_listener(self)

    def on_message(self, message):
        print message
        self.application.pc.send_message(message)

class PikaClient(object):
    def __init__(self, io_loop):
        pika.log.info('PikaClient: __init__')
        self.io_loop = io_loop
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None
        self.event_listeners = set([])
 
    def connect(self):
        if self.connecting:
            pika.log.info('PikaClient: Already connecting to RabbitMQ')
            return
 
        pika.log.info('PikaClient: Connecting to RabbitMQ')
        self.connecting = True
 
        #cred = pika.PlainCredentials('guest', 'guest')
        param = pika.ConnectionParameters(
            host='115.146.93.175',
            #port=5672,
            #virtual_host='/',
            #credentials=cred
        )
 
        self.connection = TornadoConnection(param,
            on_open_callback=self.on_connected)
        self.connection.add_on_close_callback(self.on_closed)
 
    def on_connected(self, connection):
        pika.log.info('PikaClient: connected to RabbitMQ')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)
 
    def on_channel_open(self, channel):
        pika.log.info('PikaClient: Channel open, Declaring exchange')
        self.channel = channel
        self.channel.queue_declare(queue='hello')
        self.channel.basic_consume(self.on_message,
                      queue='hello',
                      no_ack=True)
        # declare exchanges, which in turn, declare
        # queues, and bind exchange to queues
 
    def on_closed(self, connection):
        pika.log.info('PikaClient: rabbit connection closed')
        self.io_loop.stop()
 
    def on_message(self, channel, method, header, body):
        pika.log.info('PikaClient: message received: %s' % body)
        self.notify_listeners(body)

    def send_message(self, body):
        self.channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=body)
 
    def notify_listeners(self, body):
        for listener in self.event_listeners:
            listener.write_message(body)
            pika.log.info('PikaClient: notified %s' % repr(listener))
 
    def add_event_listener(self, listener):
        print "added listener"
        self.event_listeners.add(listener)
        pika.log.info('PikaClient: listener %s added' % repr(listener))
 
    def remove_event_listener(self, listener):
        try:
            self.event_listeners.remove(listener)
            pika.log.info('PikaClient: listener %s removed' % repr(listener))
        except KeyError:
            pass

application = tornado.web.Application([
    (r'/ws', MyWebSocketHandler),
])
 
def main():
    pika.log.setup(color=True)
    io_loop = tornado.ioloop.IOLoop.instance()
    # PikaClient is our rabbitmq consumer
    pc = PikaClient(io_loop)
    application.pc = pc
    application.pc.connect()
    application.listen(8888)
    io_loop.start()

if __name__ == '__main__':
    main()

