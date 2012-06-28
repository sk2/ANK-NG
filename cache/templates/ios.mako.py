# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 8
_modified_time = 1340861795.907303
_enable_loop = True
_template_filename = '/Users/sk2/Dropbox/PhD/Dev/ANK-NG/templates/ios.mako'
_template_uri = 'templates/ios.mako'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        node = context.get('node', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'hostname ')
        __M_writer(unicode(node))
        __M_writer(u'\n!\nboot-start-marker\nboot-end-marker\n!\n!\nno aaa new-model\n!\n!\nip cef\n! \n!      \nservice timestamps debug datetime msec\nservice timestamps log datetime msec\nno service password-encryption\nenable password cisco\nip classless\nip subnet-zero\nno ip domain lookup\nline vty 0 4\n exec-timeout 720 0\n password cisco\n login\nline con 0\n password cisco\n!\n')
        # SOURCE LINE 27
        for interface in node.interfaces:  
            # SOURCE LINE 28
            __M_writer(u'interface ')
            __M_writer(unicode(interface.id))
            __M_writer(u'\n\tdescription ')
            # SOURCE LINE 29
            __M_writer(unicode(interface.description))
            __M_writer(u'\n\tip address ')
            # SOURCE LINE 30
            __M_writer(unicode(interface.ip_address))
            __M_writer(u' ')
            __M_writer(unicode(interface.subnet.netmask))
            __M_writer(u'   \n')
            # SOURCE LINE 31
            if interface.ospf_cost:
                # SOURCE LINE 32
                __M_writer(u'\tip ospf cost ')
                __M_writer(unicode(interface.ospf_cost))
                __M_writer(u'\n')
                pass
            # SOURCE LINE 34
            __M_writer(u'\tno shutdown\n   \tduplex auto\n\tspeed auto\n!\n')
            pass
        # SOURCE LINE 39
        __M_writer(u'!               \n')
        # SOURCE LINE 40
        if node.ospf: 
            # SOURCE LINE 41
            __M_writer(u'router ospf ')
            __M_writer(unicode(node.ospf.process_id))
            __M_writer(u' \n  network ')
            # SOURCE LINE 42
            __M_writer(unicode(node.loopback))
            __M_writer(u' 0.0.0.0 area 0\n  log-adjacency-changes\n  passive-interface Loopback0\n')
            # SOURCE LINE 45
            for ospf_link in node.ospf.ospf_links:
                # SOURCE LINE 46
                __M_writer(u'  network ')
                __M_writer(unicode(ospf_link.network.network))
                __M_writer(u' ')
                __M_writer(unicode(ospf_link.network.hostmask))
                __M_writer(u' area ')
                __M_writer(unicode(ospf_link.area))
                __M_writer(u' \n')
                pass
            pass
        # SOURCE LINE 49
        if node.isis: 
            # SOURCE LINE 50
            __M_writer(u'router isis ')
            __M_writer(unicode(node.isis.process_id))
            __M_writer(u'       \n')
            pass
        # SOURCE LINE 52
        if node.eigrp: 
            # SOURCE LINE 53
            __M_writer(u'router eigrp ')
            __M_writer(unicode(node.eigrp.process_id))
            __M_writer(u'       \n')
            pass
        # SOURCE LINE 55
        __M_writer(u'!\n!                \n')
        # SOURCE LINE 101
        __M_writer(u'  \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


