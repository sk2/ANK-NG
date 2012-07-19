import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import glob
from networkx.readwrite import json_graph
import pickle
import ank
#TODO use cPickle

class MyServer(HTTPServer):
    #TODO: inherit __init__

#TODO: use @property for setters/getters here

    def get_anm(self):
        #TODO: Store directory from __init__ argument rather than hard-coded
        directory = os.path.join("versions", "anm")
        glob_dir = os.path.join(directory, "*.pickle.tar.gz")
        pickle_files = glob.glob(glob_dir)
        pickle_files = sorted(pickle_files)
# check if most recent outdates current most recent
        latest_file = pickle_files[-1]
#TODO: put this in __init__
        try:
            self.latest_file
        except AttributeError:
            self.latest_file = None
        if self.latest_file != latest_file:
# new latest file
            self.latest_file = latest_file
            with open(latest_file, "r") as latest_fh:
                anm = pickle.load(latest_fh)
                self.anm = anm
        return self.anm

    def get_overlay(self, overlay):
        return self.anm[overlay]

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            #TODO: handle "/" and return index.html
            if self.path == "/":
                self.path = "/index.html"

            pathparts = self.path.split("/")

            if pathparts[1] == "data":
                overlay_id = pathparts[2]
                overlay_graph = self.server.get_overlay(overlay_id)._graph.copy()
                graphics_graph = self.server.get_overlay("graphics")._graph.copy()
                overlay_graph = ank.stringify_netaddr(overlay_graph)
# JSON writer doesn't handle 'id' already present in nodes
                #for n in graph:
                    #del graph.node[n]['id']


                for n in overlay_graph:
                    overlay_graph.node[n].update( {
                        'x': graphics_graph.node[n]['x'],
                        'y': graphics_graph.node[n]['y'],
                        'device_type': graphics_graph.node[n]['device_type'],
                        })


# strip out graph data
                overlay_graph.graph = {}

                data = json_graph.dumps(overlay_graph)
                self.send_response(200)
                self.send_header('Content-type',    'text/json')
                self.end_headers()
                self.wfile.write(data)
                return


# server up overlay
            else:
                #TODO: use os path join here
                stripped_path = self.path[1:] #TODO: See how BaseHTTPServer does this for example
                file_location = os.path.join(os.getcwd(), "ank_vis", stripped_path)
#note that this potentially makes every file on your computer readable by the internet
                f = open(file_location, "r")
                print "Serving", stripped_path

                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return


            #TODO: if .js transfer as MIME type script

        except IOError:
            print "not found", self.path
            
            

def main():
    PORT = 8000

    try:
        server = MyServer(('', PORT), MyHandler)
        server.get_anm()
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

