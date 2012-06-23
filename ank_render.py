import mako
from mako.lookup import TemplateLookup
from mako.exceptions import SyntaxException
import os
import threading
import Queue
import time

#TODO: fix support here for template lookups, internal, user provided
#template_cache_dir = config.template_cache_dir
template_cache_dir = "cache"

lookup = TemplateLookup(directories=[""],
                        module_directory= template_cache_dir,
                        cache_type='memory',
                        cache_enabled=True,
                       )

#TODO: Add support for both src template and src folder (eg for quagga, servers)
def render_node(node):
        try:
            render_output_dir = node.render.dst_folder
            render_template_file = node.render.template
            dst_file = os.path.join(node.render.dst_folder, node.render.dst_file)
        except KeyError, error:
            #print "Skipping render for %s: %s not set" % (node, error)
            #TODO: log to debug
            return

        try:
            render_template = lookup.get_template(render_template_file)
        except SyntaxException, error:
            print "Unable to render %s: Syntax error in template: %s" % (node, error)
            return

#TODO: may need to iterate if multiple parts of the directory need to be created
        if not os.path.isdir(render_output_dir):
            os.mkdir(render_output_dir)

        #TODO: capture mako errors better

        with open( dst_file, 'wb') as dst_fh:
            try:
                dst_fh.write(render_template.render(
                    node = node,
                    ))
            except KeyError, error:
                print "Unable to render %s: %s not set" % (node, error)
            except AttributeError, error:
                print "Unable to render %s: %s " % (node, error)
            except NameError, error:
                print "Unable to render %s: %s. Check all variables used are defined" % (node, error)

        return

"""
def render(nidb):
    for node in nidb:
        render_node(node)
"""

def render(nidb):
        nidb_node_count = len(nidb)
        num_worker_threads = 20
        rendered_nodes = []
        def worker():
                while True:
                    node = q.get()
                    render_node(node)
                    q.task_done()
                    rendered_nodes.append(node.label)

        q = Queue.Queue()

        for i in range(num_worker_threads):
            t = threading.Thread(target=worker)
            t.setDaemon(True)
            t.start()

        # Sort so starup looks neater
#TODO: fix sort
        for node in nidb:
            q.put(node)

        while True:
            """ Using this instead of q.join allows easy way to quit all threads (but not allow cleanup)
            refer http://stackoverflow.com/questions/820111"""
            time.sleep(1)
            if len(rendered_nodes) == nidb_node_count:
# all routers started
                break
            else:
                #print "rendered", len(rendered_nodes)
                pass
