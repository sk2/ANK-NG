# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1340447051.318089
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
        __M_writer(u'    \n\n                 \n')
        # SOURCE LINE 6
        for interface in node.interfaces:  
            # SOURCE LINE 7
            __M_writer(u'interface ')
            __M_writer(unicode(interface.id))
            __M_writer(u'\n\tdescription ')
            # SOURCE LINE 8
            __M_writer(unicode(interface.description))
            __M_writer(u'\n\tip address ')
            # SOURCE LINE 9
            __M_writer(unicode(interface.ip_address))
            __M_writer(u' ')
            __M_writer(unicode(interface.subnet.netmask))
            __M_writer(u'   \n')
            # SOURCE LINE 10
            if interface.ospf_cost:
                # SOURCE LINE 11
                __M_writer(u'\tip ospf cost ')
                __M_writer(unicode(interface.ospf_cost))
                __M_writer(u'\n')
                pass
            # SOURCE LINE 13
            __M_writer(u'\tno shutdown\n   \tduplex auto\n\tspeed auto\n!\n')
            pass
        return ''
    finally:
        context.caller_stack._pop_frame()


