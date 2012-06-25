import string,cgi,time
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
import json

class MyServer(HTTPServer):
    #TODO: inherit __init__

    def set_overlay(self, overlay_graph):
        self.overlay_graph = overlay_graph

    def get_overlay(self):
        return self.overlay_graph


class MyHandler(BaseHTTPRequestHandler):



    def do_GET(self):
        try:
            if self.path.endswith("data.json"):
                print self.path
                overlay_graph = self.server.get_overlay()
                graph = overlay_graph._graph.copy()
                for node in overlay_graph:
                    graph.node[node.node_id]['label'] = node.overlay.input.label
                    graph.node[node.node_id]['x'] = node.overlay.graphics.x
                    graph.node[node.node_id]['y'] = node.overlay.graphics.y

                for node, data in graph.nodes(data=True):
                    add_nodes = {'an': {node: {'label': data['label']}}}
                    data =  json.dumps(add_nodes)
                    print data

# server up overlay
            else:
                #TODO: use os path join here
                stripped_path = self.path[1:] #TODO: See how BaseHTTPServer does this for example
                file_location = os.path.join(os.getcwd(), "vis", stripped_path)
#note that this potentially makes every file on your computer readable by the internet
                f = open(file_location, "r")

                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
            
            




def stream(overlay_graph):
    import json
    import urllib2

    PORT = 8000

    try:
        server = MyServer(('', PORT), MyHandler)
        server.set_overlay(overlay_graph)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
    url = "http://localhost:8080/workspace0?operation=getGraph"
    #req = urllib2.Request(url, data, {'Content-Type': 'application/json'})


    return


    graph = overlay_graph._graph.copy()
    for node in overlay_graph:
        graph.node[node.node_id]['label'] = node.overlay.input.label
        graph.node[node.node_id]['x'] = node.overlay.graphics.x
        graph.node[node.node_id]['y'] = node.overlay.graphics.y

    for node, data in graph.nodes(data=True):
        add_nodes = {'an': {node: {'label': data['label']}}}
        data =  json.dumps(add_nodes)
        print data
        print 'curl "http://localhost:8080/workspace0?operation=updateGraph" -d "%s"' % data
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        #response = f.read()
        f.close()
        #print response
    #add_edges = {'ae':data['links']}
    #print 'curl "http://localhost:8080/workspace0?operation=updateGraph -d "%s"' % pprint.pformat(add_nodes)
    #pprint.pformat(add_edges)
