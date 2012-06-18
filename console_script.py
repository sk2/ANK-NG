from anm import AbstractNetworkModel
import ank

anm = AbstractNetworkModel()
input_graph = ank.load_graphml("example.graphml")

G_in = anm.add_overlay("input", input_graph)

#G_phy created automatically by ank
G_phy = anm.overlay.phy

# build physical graph
G_phy.add_nodes_from(G_in, retain=['label'])

#G_phy.dump()

G_ip = anm.add_overlay("ip")
G_igp = anm.add_overlay("igp")
G_bgp = anm.add_overlay("bgp")

G_bgp.add_nodes_from([d for d in G_in if d.device_type == "router"])

# eBGP
ebgp_edges = [edge for edge in G_in.edges() if edge.src.asn != edge.dst.asn]
G_bgp.add_edges_from(ebgp_edges, default={'type': 'ebgp'})

# now iBGP
for asn, devices in G_in.groupby("asn").items():
    #print "iBGP for asn", asn

    asn_subgraph = G_in.subgraph(devices, name="asn%s" % asn)

    routers = [d for d in devices if d.device_type == "router"]
    ibgp_edges = [ (s, t) for s in routers for t in routers if s!=t]
    G_bgp.add_edges_from(ibgp_edges, default={'type': 'ibgp'})

# mark nodes according to properties

ebgp_nodes = [d for d in G_bgp if any(edge.type == 'ebgp' for edge in d.edges())]
print "ebgp nodes are", ebgp_nodes
G_bgp.update(ebgp_nodes, ebgp=True)
print [d.ebgp for d in G_bgp]
    
G_bgp.dump()
#ank.plot(G_bgp, edge_label_attribute="type")
#plot(G_phy)
#save(G_bgp)
