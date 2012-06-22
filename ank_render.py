import mako
from mako.lookup import TemplateLookup
from mako.exceptions import SyntaxException
import os

#TODO: fix support here for template lookups, internal, user provided
#template_cache_dir = config.template_cache_dir

lookup = TemplateLookup(directories=[""],
                        #module_directory= template_cache_dir,
                        #cache_type='memory',
                        #cache_enabled=True,
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

def render(nidb):
    for node in nidb:
        render_node(node)
