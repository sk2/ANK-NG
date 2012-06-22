from mako.lookup import TemplateLookup
import os
import threading
import Queue
import time


#TODO: fix support here for template lookups, internal, user provided
#template_cache_dir = config.template_cache_dir

lookup = TemplateLookup(directories=[""],
                        #module_directory= template_cache_dir,
                        #cache_type='memory',
                        #cache_enabled=True,
                       )

#TODO: Add support for both src template and src folder (eg for quagga, servers)
def render_node(node):
        render_output_dir = node.render.dst_folder
#TODO: may need to iterate if multiple parts of the directory need to be created
        if not os.path.isdir(render_output_dir):
            os.mkdir(render_output_dir)

        render_template = lookup.get_template(node.render.template)
        dst_file = os.path.join(node.render.dst_folder, node.render.dst_file)
        with open( dst_file, 'wb') as dst_fh:
            dst_fh.write(render_template.render(
                node = node,
                ))

        return

def render(nidb):
        nidb_node_count = len(nidb)
        num_worker_threads = 5
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
                print "rendered", len(rendered_nodes)


