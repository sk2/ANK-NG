import networkx as nx
from anm import overlay_node, overlay_edge
from collections import defaultdict
import itertools
import pprint
import time
import json
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

def fqdn(node):
    return "%s.%s" % (node.label, node.asn)

def name_folder_safe(foldername):
    for illegal_char in [" ", "/", "_", ",", ".", "&amp;", "-", "(", ")"]:
        foldername = foldername.replace(illegal_char, "_")
    # Don't want double _
    while "__" in foldername:
        foldername = foldername.replace("__", "_")
    return foldername

#TODO: have function that goes over a list, edge edges_to_add and sets edge_id if not set
#this cleans up the manual edge adding process

def set_node_default(overlay_graph, nbunch, **kwargs):
    """Sets all nodes in nbunch to value if key not already set"""
    graph = unwrap_graph(overlay_graph)
    nbunch = unwrap_nodes(nbunch)
    for node in nbunch:
        for key, val in kwargs.items():
            if key not in graph.node[node]:
                graph.node[node][key] = val

def load_graphml(filename):
    import string
    import os

    """
    pickle_dir = os.getcwd() + os.sep + "cache"
    if not os.path.isdir(pickle_dir):
        os.mkdir(pickle_dir)

    path, file_with_ext = os.path.split(filename)
    file_name_only, extension = os.path.splitext(filename)

    pickle_file = "%s/%s.pickle" % (pickle_dir, file_name_only)
    if (os.path.isfile(pickle_file) and
        os.stat(filename).st_mtime < os.stat(pickle_file).st_mtime):
        # Pickle file exists, and source_file is older
        graph = nx.read_gpickle(pickle_file)
    else:
        # No pickle file, or is outdated
        try:
            graph = nx.read_graphml(filename)
        except IOError:
            print "Unable to read GraphML", filename
            return
        nx.write_gpickle(graph, pickle_file)
#TODO: node labels if not set, need to set from a sequence, ensure unique... etc
    """
    try:
        graph = nx.read_graphml(filename)
    except IOError:
        print "Unable to read GraphML", filename
        return
    graph.graph['timestamp'] =  os.stat(filename).st_mtime

    # remove selfloops
    graph.remove_edges_from(edge for edge in graph.selfloop_edges())

    letters_single = (c for c in string.lowercase) # a, b, c, ... z
    letters_double = ("%s%s" % (a, b) for (a, b) in itertools.product(string.lowercase, string.lowercase)) # aa, ab, ... zz
    letters = itertools.chain(letters_single, letters_double) # a, b, c, .. z, aa, ab, ac, ... zz
#TODO: need to get set of current labels, and only return if not in this set

    #TODO: add cloud, host, etc
    # prefixes for unlabelled devices, ie router -> r_a
    label_prefixes = {
            'router': 'r',
            'switch': 'sw',
            'server': 'se',
            }

    current_labels = set(graph.node[node].get("label") for node in graph.nodes_iter())
    unique_label = (letter for letter in letters if letter not in current_labels)

# set our own defaults if not set
#TODO: store these in config file
    ank_node_defaults = {
            'asn': 1,
            'device_type': 'router'
            }
    node_defaults = graph.graph['node_default']
    for key, val in ank_node_defaults.items():
        if key not in node_defaults or node_defaults[key] == "None":
            node_defaults[key] = val

    for node in graph:
        for key, val in node_defaults.items():
            if key not in graph.node[node]:
                graph.node[node][key] = val

    # and ensure asn is integer, x and y are floats
    for node in graph:
        graph.node[node]['asn'] = int(graph.node[node]['asn'])
        try:
            x = float(graph.node[node]['x'])
        except KeyError:
            x = 0
        graph.node[node]['x'] = x
        try:
            y = float(graph.node[node]['y'])
        except KeyError:
            y = 0
        graph.node[node]['y'] = y
        try:
            graph.node[node]['label']
        except KeyError:
            device_type = graph.node[node]['device_type']
            graph.node[node]['label'] = "%s_%s" % (label_prefixes[device_type], unique_label.next())

    ank_edge_defaults = {
            'type': 'physical',
            }
    edge_defaults = graph.graph['edge_default']
    for key, val in ank_edge_defaults.items():
        if key not in edge_defaults or edge_defaults[key] == "None":
            edge_defaults[key] = val

    for src, dst in graph.edges():
        for key, val in edge_defaults.items():
            if key not in graph[src][dst]:
                graph[src][dst][key] = val

    # allocate edge_ids
    for src, dst in graph.edges():
        graph[src][dst]['edge_id'] = "%s_%s" % (graph.node[src]['label'], graph.node[dst]['label'])

# apply defaults
# relabel nodes
#other handling... split this into seperate module!
# relabel based on label: assume unique by now!
    mapping = dict( (n, d['label']) for n, d in graph.nodes(data=True))
    nx.relabel_nodes(graph, mapping, copy=False)
    return graph


def stringify_netaddr(graph):
    import netaddr
# converts netaddr from iterables to strings so can use with json
    replace_as_string = set([netaddr.ip.IPAddress, netaddr.ip.IPNetwork])
#TODO: see if should handle dict specially, eg expand to __ ?

    for key, val in graph.graph.items():
        if type(val) in replace_as_string:
            graph.graph[key] = str(val)

    for node, data in graph.nodes(data=True):
        for key, val in data.items():
            if type(val) in replace_as_string:
                graph.node[node][key] = str(val)

    for src, dst, data in graph.edges(data=True):
        for key, val in data.items():
            if type(val) in replace_as_string:
                graph[src][dst][key] = str(val)

    return graph

def save(overlay_graph):
    import netaddr
    graph = overlay_graph._graph.copy() # copy as want to annotate

# and put in basic attributes
    for node in overlay_graph:
        data = {}
        data['label'] = node.label
        #TODO: make these come from G_phy instead
        #graph.node[node.node_id]['label'] = node.overlay.input.label
        #graph.node[node.node_id]['device_type'] = node.overlay.input.device_type
        graph.node[node.node_id]['device_type'] = node.overlay.graphics.device_type
        graph.node[node.node_id]['x'] = node.overlay.graphics.x
        graph.node[node.node_id]['y'] = node.overlay.graphics.y

        graph.node[node.node_id].update(data)
#TODO: tidy this up

    replace_as_string = set([type(None), netaddr.ip.IPAddress, netaddr.ip.IPNetwork, dict, defaultdict])
#TODO: see if should handle dict specially, eg expand to __ ?

    for key, val in graph.graph.items():
        if type(val) in replace_as_string:
            graph.graph[key] = str(val)

    for node, data in graph.nodes(data=True):
        for key, val in data.items():
            if type(val) in replace_as_string:
                graph.node[node][key] = str(val)

    for src, dst, data in graph.edges(data=True):
        for key, val in data.items():
            if type(val) in replace_as_string:
                graph[src][dst][key] = str(val)

    mapping = dict( (n.node_id, str(n)) for n in overlay_graph) 
    nx.relabel_nodes( graph, mapping, copy=False)
#TODO: See why getting networkx.exception.NetworkXError: GraphML writer does not support <type 'NoneType'> as data values.
#TODO: process writer to allow writing of IPnetwork class values
    filename = "%s.graphml" % overlay_graph.name
    nx.write_graphml(graph, filename)

# probably want to create a graph from input with switches expanded to direct connections

#TODO: make edges own module
def wrap_edges(overlay_graph, edges):
    """ wraps node ids into edge overlay """
    return ( overlay_edge(overlay_graph._anm, overlay_graph._overlay_id, src, dst)
            for src, dst in edges)

def wrap_nodes(overlay_graph, nodes):
    """ wraps node id into node overlay """
    return ( overlay_node(overlay_graph._anm, overlay_graph._overlay_id, node)
            for node in nodes)

#TODO: use these wrap and unwrap functions inside overlays
def unwrap_nodes(nodes):
    try:
        return nodes.node_id # treat as single node
    except AttributeError:
        return (node.node_id for node in nodes) # treat as list

def unwrap_edges(edges):
    return ( (edge.src_id, edge.dst_id) for edge in edges)

def unwrap_graph(overlay_graph):
    return overlay_graph._graph

def in_edges(overlay_graph, nodes=None):
    graph = unwrap_graph(overlay_graph)
    edges = graph.in_edges(nodes)
    return wrap_edges(overlay_graph, edges)

def split(overlay_graph, edges, retain = []):
    try:
        retain.lower()
        retain = [retain] # was a string, put into list
    except AttributeError:
        pass # already a list

    graph = unwrap_graph(overlay_graph)
    edges = list(unwrap_edges(edges))
    edges_to_add = []
    added_nodes = []
    for (src, dst) in edges:
        cd_id = "cd_%s_%s" % (src, dst)
        data = dict( (key, graph[src][dst][key]) for key in retain)
        edges_to_add.append( (src, cd_id, data))
        edges_to_add.append( (dst, cd_id, data))
        added_nodes.append(cd_id)

    graph.remove_edges_from(edges)
    graph.add_edges_from(edges_to_add)

    return wrap_nodes(overlay_graph, added_nodes)

def explode_nodes(overlay_graph, nodes, retain = []):
    """Explodes all nodes in nodes
    TODO: explain better
    """
    try:
        retain.lower()
        retain = [retain] # was a string, put into list
    except AttributeError:
        pass # already a list

    graph = unwrap_graph(overlay_graph)
    nodes = unwrap_nodes(nodes)
    added_edges = []
#TODO: need to keep track of edge_ids here also?
    nodes = list(nodes)
    for node in nodes:
        neighbors = graph.neighbors(node)
        neigh_edge_pairs = ( (s,t) for s in neighbors for t in neighbors if s != t)
        edges_to_add = []
        for (src, dst) in neigh_edge_pairs:
            data = dict( (key, graph[src][dst][key]) for key in retain)
            edges_to_add.append((src, dst, data))

        graph.add_edges_from(edges_to_add)
        added_edges.append(edges_to_add)

        graph.remove_node(node)

    return wrap_edges(overlay_graph, added_edges)

def label(overlay_graph, nodes):
    return list(overlay_graph._anm.node_label(node) for node in nodes)

def aggregate_nodes(overlay_graph, nodes, retain = []):
    """Combines connected into a single node"""
    try:
        retain.lower()
        retain = [retain] # was a string, put into list
    except AttributeError:
        pass # already a list

    nodes = list(unwrap_nodes(nodes))
    graph = unwrap_graph(overlay_graph)
    subgraph = graph.subgraph(nodes)
    if not len(subgraph.edges()):
        #print "Nothing to aggregate for %s: no edges in subgraph"
        pass
    total_added_edges = []
    for component_nodes in nx.connected_components(subgraph):
        if len(component_nodes) > 1:
            base = component_nodes.pop() # choose one base device to retain
            nodes_to_remove = set(component_nodes) # remaining nodes, set for fast membership test
            external_edges = nx.edge_boundary(graph, component_nodes)
            edges_to_add = []
            for src, dst in external_edges:
                # src is the internal node to remove
                if src == base or dst == base:
                    continue # don't alter edges from base
                else:
                    if src in nodes_to_remove:
                        # edge from component to outside
                        data = dict( (key, graph[src][dst][key]) for key in retain)
                        edges_to_add.append((base, dst, data))
                    else:
                        # edge from outside into component
                        data = dict( (key, graph[dst][src][key]) for key in retain)
                        edges_to_add.append((base, src, data))
            graph.add_edges_from(edges_to_add)
            total_added_edges += edges_to_add
            graph.remove_nodes_from(nodes_to_remove)

    return wrap_edges(overlay_graph, total_added_edges)

# chain of two or more nodes

def most_frequent(iterable):
    """returns most frequent item in iterable"""
    unique = set(iterable)
    sorted_values = [val for val in sorted(unique, key = iterable.count)]
    return sorted_values.pop() # most frequent is at end of sorted list

def neigh_average(overlay_graph, node, attribute, attribute_graph = None):
    """ averages out attribute from neighbors in specified overlay_graph
    attribute_graph is the graph to read the attribute from
    if property is numeric, then return mean
        else return most frequently occuring value
    """
    graph = unwrap_graph(overlay_graph)
    if attribute_graph:
        attribute_graph = unwrap_graph(attribute_graph)
    else:
        attribute_graph = graph # use input graph
    node = unwrap_nodes(node)
    values = [attribute_graph.node[n].get(attribute) for n in graph.neighbors(node)]
#TODO: use neigh_attr
    try:
        values = [float(val) for val in values]
        return sum(values)/len(values)
    except ValueError:
        return most_frequent(values)

def neigh_attr(overlay_graph, node, attribute, attribute_graph = None):
    #TODO: tidy up parameters to take attribute_graph first, and then evaluate if attribute_graph set, if not then use attribute_graph as attribute
    """Boolean, True if neighbors in overlay_graph all have same attribute in attribute_graph"""
    graph = unwrap_graph(overlay_graph)
    node = unwrap_nodes(node)
    if attribute_graph:
        attribute_graph = unwrap_graph(attribute_graph)
    else:
        attribute_graph = graph # use input graph

    #Only look at nodes which exist in attribute_graph
    neighs = (n for n in graph.neighbors(node))
    valid_nodes = (n for n in neighs if n in attribute_graph)
    return (attribute_graph.node[node].get(attribute) for node in valid_nodes)

def neigh_equal(overlay_graph, node, attribute, attribute_graph = None):
    neigh_attrs = neigh_attr(overlay_graph, node, attribute, attribute_graph)
    return len(set(neigh_attrs)) == 1

def unique_attr(overlay_graph, attribute):
    graph = unwrap_graph(overlay_graph)
    return set(graph.node[node].get(attribute) for node in graph)


#TODO: move subnet to another module

def subnet_size(host_count):
    """Returns subnet size"""
    import math
    host_count += 2 # network and broadcast
    return int(math.ceil(math.log(host_count, 2)))

class Tree:
    def __init__(self, root_node, asn):
        self.timestamp =  time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.root_node = root_node
        self.asn = asn

    def __getstate__(self):
        """For pickling"""
        return (self.timestamp, self.root_node, self.asn)

    def __setstate__(self, state):
        """For pickling"""
        (timestamp, root_node, asn) = state
        self.timestamp = timestamp
        self.root_node = root_node
        self.asn = asn


    def save(self):
#TODO: try cPickle
        pickle_dir = os.path.join("versions", "ip")
        if not os.path.isdir(pickle_dir):
            os.makedirs(pickle_dir)

        pickle_file = "ip_as%s_%s.pickle.tar.gz" % (self.asn, self.timestamp)
        pickle_path = os.path.join(pickle_dir, pickle_file)
        with open(pickle_path, "wb") as pickle_fh:
            pickle.dump(self, pickle_fh, -1)

    def __str__(self):
        print self.walk_tree(self.root_node)

    def dump(self):
        print self.walk_tree(self.root_node)

    def json(self):
        return json.dumps(self._json_element(self.root_node), indent=4)

    def _json_element(self, node):
        #TODO: need to case IP addresses to string for JSON
        nodes = []
        if node.left:
            nodes.append(self._json_element(node.left))
        if node.right:
            nodes.append(self._json_element(node.right))
        if nodes:
            return {
                    "name": str(node),
                    "children": nodes,
                }

        return {"name": str(node)}


    def walk_tree(self, node):
        #TODO: combine this with JSON and printing
        if node.left:
            walk_tree(node.left)
        print node
        if node.right:
            walk_tree(node.right)

class TreeNode:
    """Adapted from http://stackoverflow.com/questions/2078669"""
    def __init__(self,left=None,right=None, cd = None):
        self.left=left
        self.right=right
        self.subnet = None
        self.cd = cd

    @property
    def leaf(self):
        """If this node has any children"""
        if not self.left and not self.right:
            return True
        return False

    def __repr__(self):
        if self.cd:
            return '(%s %s)' % ( self.subnet, self.cd)

        return str(self.subnet)

def allocate_to_tree_node(node):
    node_subnet = node.subnet
    #print "node", node, "has subnet", node_subnet
# divide into two
    child_subnets = node_subnet.subnet(node_subnet.prefixlen+1)
    if node.left:
        node.left.subnet = child_subnets.next()
        allocate_to_tree_node(node.left)
    if node.right:
        node.right.subnet = child_subnets.next()
        allocate_to_tree_node(node.right)

def walk_tree(node):
    if node.left:
        walk_tree(node.left)
    print node
    if node.right:
        walk_tree(node.right)

# need to be able to save and restore tree

def allocate_ips_to_cds(node):
    if node.left:
        allocate_ips_to_cds(node.left)
    if node.right:
        allocate_ips_to_cds(node.right)

    if node.cd:
        #print "node", node, "has cd", node.cd
        try:
            node.cd.subnet = node.subnet
        except AttributeError:
            if node.cd == "loopback":
                pass # expected, this is the loopback placeholder, handled seperately
            else:
                raise # something else went wrong

    
def allocate_ips(G_ip):
    from netaddr import IPNetwork
    address_block = IPNetwork("10.0.0.0/8")
    subnet_address_blocks = address_block.subnet(16)
#TODO: need to divide this up per AS

    G_ip.data.asn_blocks = defaultdict(list)
    #print G_ip._graph
    
    G_phy = G_ip.overlay.phy
    collision_domains = list(G_ip.nodes("collision_domain"))

    routers_by_asn = G_phy.groupby("asn", G_phy.nodes(device_type="router"))

    for collision_domain in collision_domains:
        neigh_asn = list(neigh_attr(G_ip, collision_domain, "asn", G_phy)) #asn of neighbors
        if len(set(neigh_asn)) == 1:
            asn = set(neigh_asn).pop() # asn of any neigh, as all same
        else:
            asn = most_frequent(neigh_asn) # allocate cd to asn with most neighbors in it
        collision_domain.asn = asn

    cds_by_asn = G_ip.groupby("asn", G_ip.nodes("collision_domain"))

# if node or subnet has IP already allocated, then skip from this tree

    for asn in routers_by_asn:
# Need to iterate by asn with routers, as single router AS may not have a cd
        asn_cds = cds_by_asn.get(asn) or []
        asn_cds = sorted(asn_cds)
#tree by ASN
#TODO: Add in loopbacks as a subnet also
        asn_address_block = subnet_address_blocks.next()
        #print "ips for asn", asn
        G_ip.data.asn_blocks[asn].append(asn_address_block)
#TODO: record this in G_ip graph data not node/edge data

        # Build list of collision domains sorted by size
        size_list = defaultdict(list)
        for cd in asn_cds:
            sn_size = subnet_size(cd.degree()) # Size of this collision domain
            size_list[sn_size].append(cd)

        loopback_size = subnet_size(len(routers_by_asn[asn])) # calculate from number of routers in asn

        ip_tree = defaultdict(list) # index by level to simplify creation of tree
        try:
            current_level = min(size_list) # start at base
        except ValueError:
            current_level = loopback_size # no cds, start at loopback
        
        asn_loopback_tree_node = None #keep track of to allocate loopbacks at end
        while True:
            cds = size_list[current_level]
            cds = sorted(cds, key = lambda x: x.node_id)
# initialse with leaves
#TODO: see if can get loopback on leftmost of tree -> then can have allocated with .1 .2 etc rather than .19 .20 etc
            ip_tree[current_level] += list(TreeNode(cd=cd) for cd in sorted(cds))
            if current_level == loopback_size:
                asn_loopback_tree_node = TreeNode(cd = "loopback")
                ip_tree[current_level].append(asn_loopback_tree_node)

            # now connect up at parent level
            tree_nodes = sorted(ip_tree[current_level]) # both leaves and parents of lower level
            pairs = list(itertools.izip(tree_nodes[::2], tree_nodes[1::2]))
            for left, right in pairs:
                ip_tree[current_level+1].append(TreeNode(left, right))
            if len(tree_nodes) % 2 == 1:
# odd number of tree nodes, add 
                final_tree_node = tree_nodes[-1]
                ip_tree[current_level+1].append(TreeNode(final_tree_node, None))

            current_level += 1
            if asn_loopback_tree_node and len(ip_tree[current_level]) < 2:
                # loopback has been allocated, and reached top of tree
                break

            #if leaf, assign back to collision domain

        # allocate to tree
        subnet_bits = 32 - max(ip_tree)
        tree_subnet = asn_address_block.subnet(subnet_bits)
        tree_root = ip_tree[max(ip_tree)].pop() # only one node at highest level (root)
        tree_root.subnet = tree_subnet.next()
        allocate_to_tree_node(tree_root)
        #walk_tree(tree_root)
        allocate_ips_to_cds(tree_root)

        my_tree = Tree(tree_root, asn)
        my_tree.save()

        # Get loopback from loopback tree node
        loopback_hosts = asn_loopback_tree_node.subnet.iter_hosts()
        #router.loopback = loopback_hosts.next()
        for router in sorted(routers_by_asn[asn], key = lambda x: x.label):
            router.overlay.ip.loopback = loopback_hosts.next()

        # now allocate to the links of each cd
        for cd in asn_cds:
            hosts = cd.subnet.iter_hosts()
            for edge in sorted(cd.edges()):
                edge.ip_address = hosts.next()

        #TODO: Also want to store this ordering of what is assigned to which node, not just the tree...

        # traverse tree, allocate back to loopbacks, and to nodes
        # TODO: should loopbacks be a sentinel type node for faster traversal rather than checking each time?

def allocate_route_reflectors(G_phy, G_bgp):
    print "allocating route reflectors"
    graph_phy = G_phy._graph
    for asn, devices in G_phy.groupby("asn").items():
        routers = [d for d in devices if d.is_router]
        router_ids = unwrap_nodes(routers)

        subgraph_phy = graph_phy.subgraph(router_ids)
        if len(subgraph_phy) == 1:  
                continue # single node in graph, no ibgp

        betw_cen = nx.degree_centrality(subgraph_phy)

        ordered = sorted(subgraph_phy.nodes(), key = lambda x: betw_cen[x], reverse = True)

        rr_count = len(subgraph_phy)/5 # Take top 20% to be route reflectors
        route_reflectors = ordered[:rr_count] # most connected 20%
        rr_clients = ordered[rr_count:] # the other routers
        route_reflectors = list(wrap_nodes(G_bgp, route_reflectors))
        rr_clients = list(wrap_nodes(G_bgp, rr_clients))

        G_bgp.update(route_reflectors, route_reflector = True) # mark as route reflector
        # rr <-> rr
        over_links = [(rr1, rr2) for rr1 in route_reflectors for rr2 in route_reflectors if rr1 != rr2] 
        G_bgp.add_edges_from(over_links, type = 'ibgp', direction = 'over')
        # client -> rr
        up_links = [(client, rr) for (client, rr) in itertools.product(rr_clients, route_reflectors)]
        G_bgp.add_edges_from(up_links, type = 'ibgp', direction = 'up')
        # rr -> client
        down_links = [(rr, client) for (client, rr) in up_links] # opposite of up
        G_bgp.add_edges_from(down_links, type = 'ibgp', direction = 'down')

    print "ibgp done"
