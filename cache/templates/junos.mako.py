# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1340454010.481748
_enable_loop = True
_template_filename = 'templates/junos.mako'
_template_uri = 'templates/junos.mako'
_source_encoding = 'ascii'
_exports = ['interface']


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        loop = __M_loop = runtime.LoopStack()
        node = context.get('node', UNDEFINED)
        def interface(data):
            return render_interface(context.locals_(__M_locals),data)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'router ')
        __M_writer(unicode(node))
        __M_writer(u'    \n')
        # SOURCE LINE 2
        loop = __M_loop._enter(node.interfaces)
        try:
            for data in loop:
                # SOURCE LINE 3
                if loop.first:
                    # SOURCE LINE 4
                    __M_writer(u'\tinterfaces {\n')
                    pass
                # SOURCE LINE 6
                __M_writer(u'    ')
                __M_writer(unicode(interface(data)))
                __M_writer(u'\n')
                # SOURCE LINE 7
                if loop.last:
                    # SOURCE LINE 8
                    __M_writer(u'}\n')
                    pass
                pass
        finally:
            loop = __M_loop._exit()
        # SOURCE LINE 11
        __M_writer(u'         \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_interface(context,data):
    __M_caller = context.caller_stack._push_frame()
    try:
        context._push_buffer()
        __M_writer = context.writer()
        # SOURCE LINE 12
        __M_writer(u'\n    interface ')
        # SOURCE LINE 13
        __M_writer(unicode(data.id))
        __M_writer(u' {\n    unit ')
        # SOURCE LINE 14
        __M_writer(unicode(data.unit))
        __M_writer(u' {\n\t    description "')
        # SOURCE LINE 15
        __M_writer(unicode(data.description))
        __M_writer(u'";\n\t    family inet  {\n\t        address ')
        # SOURCE LINE 17
        __M_writer(unicode(data.ip_address))
        __M_writer(u'/')
        __M_writer(unicode(data.subnet.prefixlen))
        __M_writer(u'   \n\t    }\n\t    } \n\t}\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


