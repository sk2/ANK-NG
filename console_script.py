from anm import AbstractNetworkModel
import ank
import itertools
from nidb import NIDB
import ank_render

anm = AbstractNetworkModel()
input_graph = ank.load_graphml("example.graphml")

G_in = anm.add_overlay("input", input_graph)

#G_phy created automatically by ank
G_phy = anm.overlay.phy

# build physical graph
#TODO: add helper function to copy across label, device_type, x, y, etc
G_phy.add_nodes_from(G_in, retain=['label', 'device_type', 'asn'])
G_phy.add_edges_from([edge for edge in G_in.edges() if edge.type == "physical"])

#TODO: need way to select nodes, eg sw1->r3
G_phy.add_edge(G_phy.node("r1"), G_phy.node("r4"))

G_graphics = anm.add_overlay("graphics") # plotting data
G_graphics.add_nodes_from(G_in, retain=['x', 'y', 'device_type'])

#TODO: add graphics interpolated for collision domain nodes

G_ip = anm.add_overlay("ip")
G_ip.add_edges_from(G_in.edges(type="physical"))

#print list(G_in.nodes())
#print list(G_in.nodes(device_type="switch"))

#explode_edges = ank.explode(G_ip, [n for n in G_ip if n.phy.device_type == "switch"])
switch_nodes = [n for n in G_ip if n.phy.device_type == "switch"]
ank.aggregate_nodes(G_ip, switch_nodes)
#TODO: add function to update edge properties: can overload node update?

#TODO: abstract this better
l3_devices = set(['router', 'server'])
edges_to_split = [edge for edge in G_ip.edges()
        if edge.src.phy.device_type in l3_devices
        and edge.dst.phy.device_type in l3_devices]
split_created_nodes = list(ank.split(G_ip, edges_to_split))
for node in split_created_nodes:
    node.overlay.graphics.x = ank.neigh_average(G_ip, node, "x", G_graphics)
    node.overlay.graphics.y = ank.neigh_average(G_ip, node, "y", G_graphics)

""" Averaging non numeric property
for node in G_phy:
    print ank.neigh_average(G_phy, node, "device_type", G_phy)

"""

#TODO: add sanity checks like only routers can cross ASes: can't have an eBGP server

switch_nodes = [n for n in G_ip if n.phy.device_type == "switch"] # regenerate due to aggregated
G_ip.update(switch_nodes, collision_domain=True) # switches are part of collision domain
G_ip.update(split_created_nodes, collision_domain=True)

# set collision domain IPs
collision_domain_id = (i for i in itertools.count(0))
for node in G_ip.nodes("collision_domain"):
    cd_id = collision_domain_id.next()
    node.cd_id = cd_id
    label = "_".join(sorted(ank.neigh_attr(G_ip, node, "label", G_phy)))
#TODO: Use this label
    if not node.is_switch:
        node.label = "cd_%s" % cd_id # switches keep their names


ank.allocate_ips(G_ip)
#print G_ip.data.asn_blocks

#G_ip.dump()
ank.save(G_ip)
#ank.plot(G_ip, edge_label_attribute="ip_address")

G_igp = anm.add_overlay("igp")

G_bgp = anm.add_overlay("bgp", directed = True)

G_bgp.add_nodes_from([d for d in G_in if d.is_router], color = 'red')

# eBGP
ebgp_edges = [edge for edge in G_in.edges() if edge.src.asn != edge.dst.asn]
G_bgp.add_edges_from(ebgp_edges, type = 'ebgp')

# now iBGP
for asn, devices in G_in.groupby("asn").items():
    #print "iBGP for asn", asn

    asn_subgraph = G_in.subgraph(devices, name="asn%s" % asn)

    routers = [d for d in devices if d.device_type == "router"]
    ibgp_edges = [ (s, t) for s in routers for t in routers if s!=t]
    G_bgp.add_edges_from(ibgp_edges, type = 'ibgp')

# mark nodes according to properties
#print "high degree nodes", [d for d in G_in if d.degree() > 2]

#for n in G_bgp:
    #print n, "has edges", list(n.edges())
    #print "in edges", list(ank.in_edges(G_bgp, n))

ebgp_nodes = [d for d in G_bgp if any(edge.type == 'ebgp' for edge in d.edges())]
#print "ebgp nodes are", ebgp_nodes
G_bgp.update(ebgp_nodes, ebgp=True)
#print [d.ebgp for d in G_bgp]

G_bgp.update([d for d in G_bgp if d.ebgp], ram = 64)

#print "big ram", list(G_bgp.filter(ram=64))
#G_phy.add_edge(G_phy.node("r3"), G_phy.node("r2"), speed=500)
    
#G_bgp.dump()
#ank.plot(G_bgp, edge_label_attribute="type")
#plot(G_phy)
ank.save(G_bgp)
ank.save(G_phy)


nidb = NIDB() 

#TODO: build this on a platform by platform basis
nidb.add_nodes_from(G_phy, retain=['label'])
for node in nidb:
    graphics_node = G_graphics.node(node) #node from graphics graph
    node.graphics.x = graphics_node.x
    node.graphics.y = graphics_node.y
    node.graphics.device_type = graphics_node.device_type

#TODO: provide abstraction to work on a list/dict easily to store/retrieve from nidb

# build BGP
for node in nidb:
    if node in G_bgp:
        bgp_node = G_bgp.node(node)
        data = []
        for session in G_bgp.edges(bgp_node):
            session_data = {}
            session_data['type'] = session.type
            data.append(session_data)
        node.bgp.session = data


for node in nidb:
    print node.bgp

for node in nidb:
    # allocate the renderer template
    node.render.template = "templates/test.mako"
    node.render.dst_folder = "rendered"
    node.render.dst_file = "%s.conf" % node.label

#ank.save(nidb)
#print nidb

for node in nidb:
    if node.bgp:
        print node, "has bgp"

ank_render.render(nidb)

# Now build the NIDB
