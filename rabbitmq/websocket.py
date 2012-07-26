import tornado.websocket as websocket

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

class Handler(WebSocketHandler):
        def open(self):
            print "New connection opened."

        def on_message(self, message):
                print message


        def on_close(self):
                print "Connection closed."


class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print "WebSocket opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket closed"

print "Server started."
HTTPServer(Application([("/", EchoWebSocket)])).listen(8888)
IOLoop.instance().start()
