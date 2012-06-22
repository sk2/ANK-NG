from anm import AbstractNetworkModel
import ank
import itertools
from nidb import NIDB
import ank_render
import time

anm = AbstractNetworkModel()
#input_graph = ank.load_graphml("example.graphml")
input_graph = ank.load_graphml("graph_combined.graphml")

G_in = anm.add_overlay("input", input_graph)

G_phy = anm.overlay.phy #G_phy created automatically by ank

# build physical graph
G_phy.add_nodes_from(G_in, retain=['label', 'device_type', 'asn'])
G_phy.add_edges_from([edge for edge in G_in.edges() if edge.type == "physical"])

#G_phy.add_edge(G_phy.node("r1"), G_phy.node("r4"))

G_graphics = anm.add_overlay("graphics") # plotting data
G_graphics.add_nodes_from(G_in, retain=['x', 'y', 'device_type'])

G_ip = anm.add_overlay("ip")
G_ip.add_nodes_from(G_in)
G_ip.add_edges_from(G_in.edges(type="physical"))

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

#TODO: add sanity checks like only routers can cross ASes: can't have an eBGP server
G_igp = anm.add_overlay("igp")
G_igp.add_nodes_from(G_in, retain=['asn'])

switch_nodes = [n for n in G_ip if n.is_switch] # regenerate due to aggregated
G_ip.update(switch_nodes, collision_domain=True) # switches are part of collision domain
G_ip.update(split_created_nodes, collision_domain=True)

# set collision domain IPs
print "collision domains"
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

print "allocating ips"
ank.allocate_ips(G_ip)
print "ips allocated"
#ank.save(G_ip)

G_bgp = anm.add_overlay("bgp", directed = True)
G_bgp.add_nodes_from([d for d in G_in if d.is_router], color = 'red')

# eBGP
ebgp_edges = [edge for edge in G_in.edges() if edge.src.asn != edge.dst.asn]
G_bgp.add_edges_from(ebgp_edges, type = 'ebgp')

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
print "allocating nidb"

nidb = NIDB() 
#TODO: build this on a platform by platform basis
nidb.add_nodes_from(G_phy, retain=['label'])
print "nidb nodes added"

#print G_ip.dump()

for node in nidb:
    phy_node = G_phy.node(node)
    for edge in phy_node.edges():
        ip_edge = G_ip.edge(edge)
        if ip_edge:
            pass
            #print ip_edge.ip_address
            #print ip_edge.dump()

print "creating nidb"
for node in nidb:
    graphics_node = G_graphics.node(node) #node from graphics graph
    node.graphics.x = graphics_node.x
    node.graphics.y = graphics_node.y
    node.graphics.device_type = graphics_node.device_type

# build IP
for node in nidb:
    if node in G_ip:
        ip_allocations = []
        for ip_link in G_ip.edges(node):
            ip_allocations.append(ip_link.ip_address)
        node.ip.allocations = ip_allocations

# build BGP
for node in nidb:
    if node in G_bgp:
        bgp_node = G_bgp.node(node)
        data = []
        asn = G_phy.node(node).asn
        node.bgp.asn_sn_blocks = G_ip.data.asn_blocks[asn]
        for session in G_bgp.edges(bgp_node):
            data.append({
                    'type': session.type,
                    'peer': session.dst,
            })
        node.bgp.session = data

        #print node.bgp['session']

for node in nidb:
    # allocate the renderer template
    node.render.template = "templates/test.mako"
    node.render.dst_folder = "rendered"
    node.render.dst_file = "%s.conf" % ank.name_folder_safe(node.label)

# and setup interfaces


#TODO: don't need to transform, just need to pass a view of the nidb which does the wrapping: iterates through returned data, recursively, and wraps accordingly. ie pass the data to return through a recursive formatter which wraps
print "rendering"
start = time.clock()
ank_render.render(nidb)
elapsed = (time.clock() - start)
print "rendering time:", elapsed

# Now build the NIDB
