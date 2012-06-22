import ank
import itertools
import netaddr

#TODO: for any property not in nidb, try and pass through to obtain from respective overlay, eg ospf tries from G_ospf.node(node) etc

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

# TODO: create base compiler class, which provides each of the Interfaces
# inherited by router compiler which does bgp, igp
# inherited by ios, etc which can then append the data they wish
# ideally calling super so don't repeat extra code, eg for description etc

def compile_ios(nidb, anm):
    G_phy = anm.overlay.phy
    G_ip = anm.overlay.ip
    G_igp = anm.overlay.igp
    G_bgp = anm.overlay.bgp
    G_graphics = anm.overlay.graphics
    loopback_subnet = netaddr.IPNetwork("0.0.0.0/32")

    print "compiling ios"
    for phy_node in G_phy.nodes('is_router', platform='ios'):
        print "ios for", phy_node
        nidb_node = nidb.node(phy_node)
        nidb_node.render.template = "templates/ios.mako"
        nidb_node.render.dst_folder = "rendered/ios"
        nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

        nidb_node.asn = phy_node.asn

#TODO: need to map interface ids
        interface_ids = ("gigabitethernet0/0/0/%s" % x for x in itertools.count(0))

        # Interfaces
        interfaces = []
        interfaces.append({
            'id': 'lo0',
            'description': "Loopback",
            'ip_address': phy_node.overlay.ip.loopback,
            'subnet': loopback_subnet,
            })

        for link in phy_node.edges():
            ip_link = G_ip.edge(link)
            #TODO: what if multiple ospf costs for this link
            ospf_cost = link.overlay.igp.cost
            subnet =  ip_link.dst.subnet # netmask comes from collision domain on the link
            data = {
                    'id': interface_ids.next(),
                    'description': "%s to %s" % (link.src, link.dst),
                    'ip_address': link.overlay.ip.ip_address,
                    'subnet': subnet,
                    'cost': ospf_cost,
                    }
            interfaces.append(data)

        #nidb_node.interfaces = interfaces
        nidb_node.interfaces = []
        
        # IGP
#TODO: check if router has IGP set as ospf or isis or ...
        nidb_node.ospf.process_id = 2
        ospf_links = []
        for igp_link in G_igp.edges(phy_node):
            ospf_links.append({
                'network': igp_link.overlay.ip.dst.subnet,
                'area': igp_link.area,
                })

        nidb_node.ospf.ospf_links = sorted(ospf_links)

        #nidb_node.eigrp.process_id = 1
        #nidb_node.isis.process_id = 1

        # BGP
        if phy_node.overlay.bgp.edges():
            asn = phy_node.asn # easy reference for cleaner code
            nidb_node.bgp.advertise_subnets = G_ip.data.asn_blocks[asn]
            igp_neighbors = []
            egp_neighbors = []
            for edge in phy_node.overlay.bgp.edges():
                print edge, edge.type
            print "ibgp edges", [edge for edge in phy_node.overlay.bgp.edges(type="ibgp")]
            print "ebgp edges", [edge for edge in phy_node.overlay.bgp.edges(type="ebgp")]
            for session in phy_node.overlay.bgp.edges():
                #TODO: design decision: more boilerplate here, or more complexity in templates?
                if session.type == 'ibgp':
                    igp_neighbors.append({
                        'neighbor': session.dst,
                        'update-source': "loopback 0",
                        })
                else:
                    egp_neighbors.append({
                        'neighbor': session.dst,
                        'update-source': "loopback 0",
                        })




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
