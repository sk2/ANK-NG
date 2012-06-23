import ank
import itertools
import netaddr

#TODO: for any property not in nidb, try and pass through to obtain from respective overlay, eg ospf tries from G_ospf.node(node) etc

def compile_junos(nidb, anm):
    G_phy = anm.overlay.phy
    G_ip = anm.overlay.ip
    G_ospf = anm.overlay.ospf
    G_bgp = anm.overlay.bgp
    G_graphics = anm.overlay.graphics

    print "compiling junos"
    for phy_node in G_phy.nodes(platform='junos'):
        nidb_node = nidb.node(phy_node)
        nidb_node.render.template = "templates/junos.mako"
        nidb_node.render.dst_folder = "rendered/junos"
        nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

# TODO: create base compiler class, which provides each of the Interfaces
# inherited by router compiler which does bgp, ospf
# inherited by ios, etc which can then append the data they wish
# ideally calling super so don't repeat extra code, eg for description etc

def compile_ios(nidb, anm):
    G_phy = anm.overlay.phy
    G_ip = anm.overlay.ip
    G_ospf = anm.overlay.ospf
    G_bgp = anm.overlay.bgp
    loopback_subnet = netaddr.IPNetwork("0.0.0.0/32")

    print "compiling ios"
    for phy_node in G_phy.nodes('is_router', platform='ios'):
        nidb_node = nidb.node(phy_node)
        nidb_node.render.template = "templates/ios.mako"
        nidb_node.render.dst_folder = "rendered/ios"
        nidb_node.render.dst_file = "%s.conf" % ank.name_folder_safe(phy_node.label)

        nidb_node.asn = phy_node.asn

#TODO: need to map interface ids
        interface_ids = ("gigabitethernet0/0/0/%s" % x for x in itertools.count(0))
        # assign interfaces
        for edge in nidb.edges(nidb_node):
            edge.id = interface_ids.next()

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
            nidb_edge = nidb.edge(link)
            #TODO: what if multiple ospf costs for this link
            ospf_cost = link.overlay.ospf.cost
            subnet =  ip_link.dst.subnet # netmask comes from collision domain on the link
            interfaces.append({
                    'id': nidb_edge.id,
                    'description': "%s to %s" % (link.src, link.dst),
                    'ip_address': link.overlay.ip.ip_address,
                    'subnet': subnet,
                    'cost': ospf_cost,
                    })

        nidb_node.interfaces = interfaces
        
        # ospf
#TODO: check if router has ospf set as ospf or isis or ...
        nidb_node.ospf.process_id = 1
        ospf_links = []
        for ospf_link in G_ospf.edges(phy_node):
            ospf_links.append({
                'network': ospf_link.overlay.ip.dst.subnet,
                'area': ospf_link.area,
                })

        nidb_node.ospf.ospf_links = sorted(ospf_links)

        # BGP
        if True:
            asn = phy_node.asn # easy reference for cleaner code
            nidb_node.bgp.advertise_subnets = G_ip.data.asn_blocks[asn]
            ibgp_neighbors = []
            ibgp_rr_clients = []
            ebgp_neighbors = []
            bgp_node = G_bgp.node(phy_node)
            for session in bgp_node.edges():
                neigh = session.dst
                if session.type == "ibgp":
                    ibgp_neighbors.append({
                        'neighbor': neigh,
                        'loopback': neigh.overlay.ip.loopback,
                        'update_source': "loopback 0",
                        })
                else:
                    ebgp_neighbors.append({
                        'neighbor': session.dst,
                        'loopback': neigh.overlay.ip.loopback,
                        'update_source': "loopback 0",
                    })

            nidb_node.bgp.ibgp_rr_clients = ibgp_rr_clients
            nidb_node.bgp.ibgp_neighbors = ibgp_neighbors
            nidb_node.bgp.ebgp_neighbors = ebgp_neighbors
