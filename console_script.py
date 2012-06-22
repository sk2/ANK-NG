from anm import AbstractNetworkModel
import ank
import itertools
from nidb import NIDB
import ank_render
import ank_compiler
import time

anm = AbstractNetworkModel()
input_graph = ank.load_graphml("example.graphml")
#input_graph = ank.load_graphml("graph_combined.graphml")

G_in = anm.add_overlay("input", input_graph)

G_phy = anm.overlay.phy #G_phy created automatically by ank

# build physical graph
G_phy.add_nodes_from(G_in, retain=['label', 'device_type', 'asn', 'platform'])
G_phy.add_edges_from([edge for edge in G_in.edges() if edge.type == "physical"])

"""
r1 = G_phy.node("r1")
r1.test = "xxx"
ank.set_node_default(G_phy, G_phy.nodes(), test="AA", color="blue")
for node in G_phy:
    print node.dump()
r1.test = "xxx"
"""

#G_phy.add_edge(G_phy.node("r1"), G_phy.node("r4"))

G_graphics = anm.add_overlay("graphics") # plotting data
G_graphics.add_nodes_from(G_in, retain=['x', 'y', 'device_type'])

G_ip = anm.add_overlay("ip")
G_ip.add_nodes_from(G_in)
G_ip.add_edges_from(G_in.edges(type="physical"))

ank.aggregate_nodes(G_ip, G_ip.nodes("is_switch"), retain = "edge_id")
#TODO: add function to update edge properties: can overload node update?

#TODO: abstract this better
edges_to_split = [edge for edge in G_ip.edges() if edge.src.is_l3device and edge.dst.is_l3device]
split_created_nodes = list(ank.split(G_ip, edges_to_split, retain='edge_id'))
for node in split_created_nodes:
    node.overlay.graphics.x = ank.neigh_average(G_ip, node, "x", G_graphics)
    node.overlay.graphics.y = ank.neigh_average(G_ip, node, "y", G_graphics)

#TODO: add sanity checks like only routers can cross ASes: can't have an eBGP server
G_ospf = anm.add_overlay("ospf")
G_ospf.add_nodes_from(G_in, retain=['asn'])
G_ospf.add_edges_from(G_in.edges(), retain = 'edge_id')
added_edges = ank.aggregate_nodes(G_ospf, G_ospf.nodes("is_switch"), retain='edge_id')

switch_nodes = G_ip.nodes("is_switch")# regenerate due to aggregated
G_ip.update(switch_nodes, collision_domain=True) # switches are part of collision domain
G_ip.update(split_created_nodes, collision_domain=True)
# allocate costs
for link in G_ospf.edges():
    link.cost = link.src.degree() # arbitrary deterministic cost
    link.area = 0

# set collision domain IPs
collision_domain_id = (i for i in itertools.count(0))
for node in G_ip.nodes("collision_domain"):
    graphics_node = G_graphics.node(node)
    graphics_node.device_type = "collision_domain"
    cd_id = collision_domain_id.next()
    node.cd_id = cd_id
    label = "_".join(sorted(ank.neigh_attr(G_ip, node, "label", G_phy)))
#TODO: Use this label
    if not node.is_switch:
        node.label = "cd_%s" % cd_id # switches keep their names
        graphics_node.label = label

ank.allocate_ips(G_ip)
#ank.save(G_ip)

G_bgp = anm.add_overlay("bgp", directed = True)
G_bgp.add_nodes_from([d for d in G_in if d.is_router], color = 'red')

# eBGP
ebgp_edges = [edge for edge in G_in.edges() if edge.src.asn != edge.dst.asn]
G_bgp.add_edges_from(ebgp_edges, bidirectional = True, type = 'ebgp')

# now iBGP
for asn, devices in G_in.groupby("asn").items():
    routers = [d for d in devices if d.device_type == "router"]
    ibgp_edges = [ (s, t) for s in routers for t in routers if s!=t]
    G_bgp.add_edges_from(ibgp_edges, type = 'ibgp')

ebgp_nodes = [d for d in G_bgp if any(edge.type == 'ebgp' for edge in d.edges())]
G_bgp.update(ebgp_nodes, ebgp=True)

#ank.save(G_bgp)
#ank.save(G_phy)

#TODO: set fqdn property

nidb = NIDB() 
#TODO: build this on a platform by platform basis
nidb.add_nodes_from(G_phy, retain=['label', 'platform'])
nidb.add_nodes_from(G_ip, retain='label', collision_domain = True)
# add edges to switches
edges_to_add = [edge for edge in G_phy.edges() if edge.src.is_switch or edge.dst.is_switch]
edges_to_add += [edge for edge in G_ip.edges() if edge.src.collision_domain or edge.dst.collision_domain]
nidb.add_edges_from(edges_to_add, retain='edge_id')

print nidb.dump()

print "cisco ndoes", list(nidb.nodes(platform="ios"))
nidb_ios = nidb.subgraph(nidb.nodes(platform="ios"))
print "ios nodes", list(nidb_ios.nodes())


#TODO: add support for nidb subgraphs, especially for platforms, and show boundary nodes and boundary edges easily


#print G_ip.dump()
"""
ank.plot_pylab(G_bgp, edge_label_attribute = 'type', node_label_attribute='asn')
ank.plot_pylab(G_phy, edge_label_attribute = 'edge_id')
ank.plot_pylab(G_ospf, edge_label_attribute='cost')
ank.plot_pylab(G_ip, edge_label_attribute = 'ip_address', node_label_attribute = 'loopback')
"""

ank_compiler.compile_ios(nidb, anm)
ank_compiler.compile_junos(nidb, anm)
# update nidb graphics
for node in nidb:
    graphics_node = G_graphics.node(node)
    node.graphics.x = graphics_node.x
    node.graphics.y = graphics_node.y
    node.graphics.device_type = graphics_node.device_type

# and setup interfaces


#TODO: don't need to transform, just need to pass a view of the nidb which does the wrapping: iterates through returned data, recursively, and wraps accordingly. ie pass the data to return through a recursive formatter which wraps
ank_render.render(nidb)

#TODO: plot the nidb
ank.plot_pylab(nidb)

# Now build the NIDB
