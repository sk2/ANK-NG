# -*- encoding:ascii -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 7
_modified_time = 1340433399.000848
_template_filename = 'templates/ios.mako'
_template_uri = 'templates/ios.mako'
_source_encoding = 'ascii'
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        node = context.get('node', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'hostname ')
        __M_writer(unicode(node))
        __M_writer(u'\n!\nboot-start-marker\nboot-end-marker\n!\n!\nno aaa new-model\n!\n!\nip cef\n! \n!      \n')
        # SOURCE LINE 13
        for interface in node.interfaces:  
            # SOURCE LINE 14
            __M_writer(u'interface ')
            __M_writer(unicode(interface.id))
            __M_writer(u'\n\tdescription ')
            # SOURCE LINE 15
            __M_writer(unicode(interface.description))
            __M_writer(u'\n\tip address ')
            # SOURCE LINE 16
            __M_writer(unicode(interface.ip_address))
            __M_writer(u' ')
            __M_writer(unicode(interface.subnet.netmask))
            __M_writer(u'   \n')
            # SOURCE LINE 17
            if interface.cost:
                # SOURCE LINE 18
                __M_writer(u'\tip ospf cost ')
                __M_writer(unicode(interface.cost))
                __M_writer(u'\n')
                pass
            # SOURCE LINE 20
            __M_writer(u'\tno shutdown\n   \tduplex auto\n\tspeed auto\n!\n')
            pass
        # SOURCE LINE 25
        __M_writer(u'!               \n')
        # SOURCE LINE 26
        if node.ospf: 
            # SOURCE LINE 27
            __M_writer(u'router ospf ')
            __M_writer(unicode(node.ospf.process_id))
            __M_writer(u' \n')
            # SOURCE LINE 28
            for ospf_link in node.ospf.ospf_links:
                # SOURCE LINE 29
                __M_writer(u'\tnetwork ')
                __M_writer(unicode(ospf_link.network.network))
                __M_writer(u' ')
                __M_writer(unicode(ospf_link.network.hostmask))
                __M_writer(u' area ')
                __M_writer(unicode(ospf_link.area))
                __M_writer(u' \n')
                pass
            pass
        # SOURCE LINE 32
        if node.isis: 
            # SOURCE LINE 33
            __M_writer(u'router isis ')
            __M_writer(unicode(node.isis.process_id))
            __M_writer(u'       \n')
            pass
        # SOURCE LINE 35
        if node.eigrp: 
            # SOURCE LINE 36
            __M_writer(u'router eigrp ')
            __M_writer(unicode(node.eigrp.process_id))
            __M_writer(u'       \n')
            pass
        # SOURCE LINE 38
        __M_writer(u'!\n!  \n')
        # SOURCE LINE 40
        if node.bgp: 
            # SOURCE LINE 41
            __M_writer(u'router bgp ')
            __M_writer(unicode(node.asn))
            __M_writer(u'   \n\tno synchronization\n')
            # SOURCE LINE 43
            for subnet in node.bgp.advertise_subnets:
                # SOURCE LINE 44
                __M_writer(u'\tnetwork ')
                __M_writer(unicode(subnet.network))
                __M_writer(u' mask ')
                __M_writer(unicode(subnet.netmask))
                __M_writer(u'                                                          \n')
                pass
            # SOURCE LINE 46
            __M_writer(u'! ibgp\n')
            # SOURCE LINE 47
            for client in node.bgp.ibgp_rr_clients:       
                # SOURCE LINE 48
                __M_writer(u'\t! ')
                __M_writer(unicode(client.neighbor))
                __M_writer(u'\n\tneighbor remote-as ')
                # SOURCE LINE 49
                __M_writer(unicode(client.neighbor.asn))
                __M_writer(u'\n\tneighbor ')
                # SOURCE LINE 50
                __M_writer(unicode(client.loopback))
                __M_writer(u' update-source ')
                __M_writer(unicode(client.update_source))
                __M_writer(u' \n\tneighbor ')
                # SOURCE LINE 51
                __M_writer(unicode(client.loopback))
                __M_writer(u' route-reflector-client                                                   \n\tneighbor send-community      \n')
                pass
            # SOURCE LINE 54
            for neigh in node.bgp.ibgp_neighbors:       
                # SOURCE LINE 55
                __M_writer(u'\t! ')
                __M_writer(unicode(neigh.neighbor))
                __M_writer(u'\n\tneighbor remote-as ')
                # SOURCE LINE 56
                __M_writer(unicode(neigh.neighbor.asn))
                __M_writer(u'\n\tneighbor ')
                # SOURCE LINE 57
                __M_writer(unicode(neigh.loopback))
                __M_writer(u' update-source ')
                __M_writer(unicode(neigh.update_source))
                __M_writer(u'                                                     \n\tneighbor send-community      \n')
                pass
            # SOURCE LINE 60
            __M_writer(u'! ebgp\n')
            # SOURCE LINE 61
            for neigh in node.bgp.ebgp_neighbors:      
                # SOURCE LINE 62
                __M_writer(u'\t! ')
                __M_writer(unicode(neigh.neighbor))
                __M_writer(u' \n\tneighbor remote-as ')
                # SOURCE LINE 63
                __M_writer(unicode(neigh.neighbor.asn))
                __M_writer(u'\n\tneighbor ')
                # SOURCE LINE 64
                __M_writer(unicode(neigh.loopback))
                __M_writer(u' update-source ')
                __M_writer(unicode(neigh.update_source))
                __M_writer(u'                                                     \n\tneighbor send-community\n')
                pass
            pass
        # SOURCE LINE 68
        __M_writer(u'!\n!\nip forward-protocol nd\n!\nno ip http server\n!')
        return ''
    finally:
        context.caller_stack._pop_frame()


