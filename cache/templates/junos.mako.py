# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1340439899.031001
_enable_loop = True
_template_filename = 'templates/junos.mako'
_template_uri = 'templates/junos.mako'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        node = context.get('node', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'JUNOS\n\nrouter ')
        # SOURCE LINE 3
        __M_writer(unicode(node))
        __M_writer(u'    \n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


