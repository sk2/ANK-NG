import ank

def compile_junos(nidb, anm):
    G_phy = anm.overlay.phy
    G_ip = anm.overlay.ip
    G_igp = anm.overlay.igp
    G_bgp = anm.overlay.bgp
    G_graphics = anm.overlay.graphics

    print "compiling junos"
    for phy_node in G_phy.nodes(platform='junos'):
        nidb_node = nidb.node(phy_node)
        print phy_node
        nidb_node.render.template = "templates/junos.mako"
        nidb_node.render.dst_folder = "rendered/junos"
        nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

def compile_ios(nidb, anm):
    G_phy = anm.overlay.phy
    G_ip = anm.overlay.ip
    G_igp = anm.overlay.igp
    G_bgp = anm.overlay.bgp
    G_graphics = anm.overlay.graphics

    print "compiling ios"
    for phy_node in G_phy.nodes('is_router', platform='ios'):
        print "ios for", phy_node
        nidb_node = nidb.node(phy_node)
        nidb_node.render.template = "templates/ios.mako"
        nidb_node.render.dst_folder = "rendered/ios"
        nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

#TODO: need to map interface ids

        # Interfaces
        interfaces = []
        for link in phy_node.edges():
            ip_link = G_ip.edge(link)
            #TODO: what if multiple ospf costs for this link
            ospf_cost = link.overlay.igp.cost
            subnet =  ip_link.dst.subnet # netmask comes from collision domain on the link
            data = {
                    'id': 'Fe/0',
                    'description': "%s to %s" % (link.src, link.dst),
                    'ip_address': link.overlay.ip.ip_address,
                    'subnet': subnet,
                    'cost': ospf_cost,
                    }
            interfaces.append(data)

        nidb_node.interfaces = interfaces
        #print nidb_node.dump()


def compile_old(nidb, anm):
    G_phy = anm.overlay.phy
    G_ip = anm.overlay.ip
    G_igp = anm.overlay.igp
    G_bgp = anm.overlay.bgp
    G_graphics = anm.overlay.graphics

    for node in nidb:
        phy_node = G_phy.node(node)
        for edge in phy_node.edges():
            ip_edge = G_ip.edge(edge)
            if ip_edge:
                pass
            #print ip_edge.ip_address
            #print ip_edge.dump()

    for node in nidb:
        graphics_node = G_graphics.node(node) #node from graphics graph
        node.graphics.x = graphics_node.x
        node.graphics.y = graphics_node.y
        node.graphics.device_type = graphics_node.device_type

# build IP
#TODO: iterate from G_phy, look up nidb_node, filter based on type
    for node in nidb:
        if node in G_ip:
            ip_allocations = []
            for ip_link in G_ip.edges(node):
                ip_allocations.append(ip_link.ip_address)
            node.ip.allocations = ip_allocations

# build IGP
        if node in G_igp:
            igp_node = G_igp.node(node)
            data = []
            for link in G_igp.edges(node):
                ip_link = G_ip.edge(link)
#TODO: allow this to return None if no data eg phy_link.int_id
                phy_link = G_phy.edge(link)
                data.append({
                    'desc': "%s to %s" % (link.src, link.dst),
                    'dest': link.dst,
                    'cost': link.cost,
                    #'phy link': phy_link.int_id,
                    'interface ip': str(ip_link.ip_address)
                    })
            node.igp.links = data

# build BGP
        if node in G_bgp:
            bgp_node = G_bgp.node(node)
            data = []
            asn = G_phy.node(node).asn
            node.bgp.asn_sn_blocks = G_ip.data.asn_blocks[asn]
            for session in G_bgp.edges(bgp_node):
                data.append({
                        'type': session.type,
                        'peer': session.dst,
                        'peer_ip': session.dst.overlay.ip.loopback,
                })
            node.bgp.session = data

            #print node.bgp['session']

    for node in nidb:
        # allocate the renderer template
        node.render.template = "templates/ios.mako"
        node.render.dst_folder = "rendered/ios"
        node.render.dst_file = "%s.conf" % ank.name_folder_safe(node.label)

    nidb.dump()
