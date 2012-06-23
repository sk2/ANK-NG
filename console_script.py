from anm import AbstractNetworkModel
import ank
import itertools
from nidb import NIDB
import ank_render
import ank_compiler
#import ank_plot

import optparse
opt = optparse.OptionParser()
opt.add_option('--file', '-f', default= None, help="Load topology from FILE")        
options, arguments = opt.parse_args()

if not options.file:
    import sys
    print "Please specify topology file using -f" #TODO: use argparse and compulsory argument
    sys.exit(0)

anm = AbstractNetworkModel()
input_graph = ank.load_graphml(options.file)
#input_graph = ank.load_graphml("graph_combined.graphml")

G_in = anm.add_overlay("input", input_graph)
ank.set_node_default(G_in, G_in.nodes(), platform="ios")

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

"""
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
"""
#ank.save(G_ip)

G_bgp = anm.add_overlay("bgp", directed = True)
G_bgp.add_nodes_from(G_in.nodes("is_router"), color = 'red')

# eBGP
ebgp_edges = [edge for edge in G_in.edges() if edge.src.asn != edge.dst.asn]
G_bgp.add_edges_from(ebgp_edges, bidirectional = True, type = 'ebgp')

# now iBGP
if len(G_phy) < 500:
# full mesh
    for asn, devices in G_phy.groupby("asn").items():
        routers = [d for d in devices if d.is_router]
        ibgp_edges = [ (s, t) for s in routers for t in routers if s!=t]
        G_bgp.add_edges_from(ibgp_edges, type = 'ibgp')
else:
    print "big graph"
    ank.allocate_route_reflectors(G_phy, G_bgp)


#TODO: probably want to use l3 connectivity graph for allocating route reflectors


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

#TODO: boundaries is still a work in progress...
ios_nodes = list(nidb.nodes(platform="ios"))

#TODO: add platform and host

#TODO: add support for nidb subgraphs, especially for platforms, and show boundary nodes and boundary edges easily


#print G_ip.dump()
"""
ank_plot.plot_pylab(G_bgp, edge_label_attribute = 'type', node_label_attribute='asn')
ank_plot.plot_pylab(G_phy, edge_label_attribute = 'edge_id')
ank_plot.plot_pylab(G_ospf, edge_label_attribute='cost')
ank_plot.plot_pylab(G_ip, edge_label_attribute = 'ip_address', node_label_attribute = 'loopback')
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
print "rendering"
ank_render.render(nidb)

#TODO: plot the nidb
#ank_plot.plot_pylab(nidb, edge_label_attribute = 'id', node_label_attribute='platform')

# Now build the NIDB
