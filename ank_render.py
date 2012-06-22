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
    for node in nidb:
        render_node(node)
