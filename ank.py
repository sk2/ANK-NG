import networkx as nx
from anm import overlay_node, overlay_edge
from collections import defaultdict
import itertools


def load_graphml(filename):
    graph = nx.read_graphml(filename)
#TODO: node labels if not set, need to set from a sequence, ensure unique... etc

#TODO: ensure unique node labels

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
        graph.node[node]['x'] = float(graph.node[node]['x'])
        graph.node[node]['y'] = float(graph.node[node]['y'])

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

# apply defaults
# relabel nodes
#other handling... split this into seperate module!
    return graph

def plot(overlay_graph, edge_label_attribute = None, save = True, show = False):
    """ Plot a graph"""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print ("Matplotlib not found, not plotting using Matplotlib")
        return
    graph = overlay_graph._graph
    graph_name = overlay_graph.name

    try:
        import numpy
    except ImportError:
        print("Matplotlib plotting requires numpy for graph layout")
        return
    
    try:
        ids, x, y = zip(*[(node.id , node.overlay.graphics.x, node.overlay.graphics.y)
                for node in overlay_graph])
        x = numpy.asarray(x, dtype=float)
        y = numpy.asarray(y, dtype=float)
#TODO: combine these two operations together
        x -= x.min()
        x *= 1.0/x.max() 
        y -= y.min()
        y *= -1.0/y.max() # invert
        y += 1 # rescale from 0->1 not 1->0
#TODO: see if can use reshape-type commands here
        co_ords = zip(list(x), list(y))
        co_ords = [numpy.array([x, y]) for x, y in co_ords]
        pos = dict( zip(ids, co_ords))
    except KeyError:
        pos=nx.spring_layout(graph)

    plt.clf()
    cf = plt.gcf()
    ax=cf.add_axes((0,0,1,1))
    # Create axes to allow adding of text relative to map
    ax.set_axis_off() 
    font_color = "k"
    node_color = "#336699"
    edge_color = "#888888"

    nodes = nx.draw_networkx_nodes(graph, pos, 
                           node_size = 50, 
                           alpha = 0.8, linewidths = (0,0),
                           node_color = node_color,
                           cmap=plt.cm.jet)

    nx.draw_networkx_edges(graph, pos, arrows=False,
                           edge_color=edge_color,
                           alpha=0.8)
    
    if edge_label_attribute:
        edge_labels = dict ( ( (edge.src.node_id, edge.dst.node_id), edge.get(edge_label_attribute))
            for edge in overlay_graph.edges())
        nx.draw_networkx_edge_labels(graph, pos, 
                            edge_labels = edge_labels,
                            font_size = 12,
                            font_color = font_color)

#TODO: where is anm from here? global? :/
    labels = dict( (n.node_id, n) for n in overlay_graph)
#TODO: need to strip out 
    nx.draw_networkx_labels(graph, pos, 
                            labels=labels,
                            font_size = 12,
                            font_color = font_color)

    title = "%s graph" % graph_name
    ax.text(0.02, 0.98, title, horizontalalignment='left',
                            weight='heavy', fontsize=16, color='k',
                            verticalalignment='top', 
                            transform=ax.transAxes)
    if show:
        plt.show()
    if save:
        filename = "%s.pdf" % graph_name
        plt.savefig(filename)

    plt.close()

def stream(overlay_graph):
    import json
    import urllib2

    proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
    url = "http://localhost:8080/workspace0?operation=getGraph"
    #req = urllib2.Request(url, data, {'Content-Type': 'application/json'})


    graph = overlay_graph._graph.copy()
    for node in overlay_graph:
        graph.node[node.node_id]['label'] = node.overlay.input.label
        graph.node[node.node_id]['x'] = node.overlay.graphics.x
        graph.node[node.node_id]['y'] = node.overlay.graphics.y

    for node, data in graph.nodes(data=True):
        add_nodes = {'an': {node: {'label': data['label']}}}
        data =  json.dumps(add_nodes)
        print data
        print 'curl "http://localhost:8080/workspace0?operation=updateGraph" -d "%s"' % data
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        #response = f.read()
        f.close()
        #print response
    #add_edges = {'ae':data['links']}
    #print 'curl "http://localhost:8080/workspace0?operation=updateGraph -d "%s"' % pprint.pformat(add_nodes)
    #pprint.pformat(add_edges)

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

    replace_as_string = set([type(None), netaddr.ip.IPAddress, netaddr.ip.IPNetwork, dict])
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

def split(overlay_graph, edges):
    from networkx.utils.misc import generate_unique_node
    graph = unwrap_graph(overlay_graph)
    edges = list(unwrap_edges(edges))
    graph.remove_edges_from(edges)
    edges_to_add = []
    added_nodes = []
    for (src, dst) in edges:
        uuid = generate_unique_node().replace("-", "")
        edges_to_add += [(src, uuid), (dst, uuid)]
        added_nodes.append(uuid)

    graph.add_edges_from(edges_to_add)

    return wrap_nodes(overlay_graph, added_nodes)

def explode(overlay_graph, nodes):
    """Explodes all nodes in nodes
    TODO: explain better
    """
    graph = unwrap_graph(overlay_graph)
    nodes = unwrap_nodes(nodes)
    added_edges = []
    for node in nodes:
        neighbors = graph.neighbors(node)
        edges_to_add = [ (s,t) for s in neighbors for t in neighbors if s != t]
        graph.add_edges_from(edges_to_add)
        added_edges.append(edges_to_add)

        graph.remove_node(node)

    return wrap_edges(overlay_graph, added_edges)

def label(overlay_graph, nodes):
    return list(overlay_graph._anm.node_label(node) for node in nodes)

def aggregate_nodes(overlay_graph, nodes):
    """Combines connected into a single node"""
    nodes = list(unwrap_nodes(nodes))
    graph = unwrap_graph(overlay_graph)
    subgraph = graph.subgraph(nodes)
    added_edges = []
    for component in nx.connected_components(subgraph):
        if len(component) > 1:
            external_nodes = nx.node_boundary(graph, component)
# choose one base device to retain
            base = component.pop()
            edges_to_add = [ (base, s) for s in external_nodes]
            added_edges.append(edges_to_add)
            graph.add_edges_from(edges_to_add)
            graph.remove_nodes_from(component)

    return wrap_edges(overlay_graph, added_edges)

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
        return '(%s %s)' % (
                self.subnet, self.cd)

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

    G_ip.data.asn_blocks = {}
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

    for asn, asn_cds in cds_by_asn.items():
#tree by ASN
#TODO: Add in loopbacks as a subnet also
        asn_address_block = subnet_address_blocks.next()
        G_ip.data.asn_blocks[asn] = asn_address_block
#TODO: record this in G_ip graph data not node/edge data

        # Build list of collision domains sorted by size
        size_list = defaultdict(list)
        for cd in asn_cds:
            sn_size = subnet_size(cd.degree()) # Size of this collision domain
            size_list[sn_size].append(cd)

        loopback_size = subnet_size(len(routers_by_asn[asn])) # calculate from number of routers in asn

        ip_tree = defaultdict(list) # index by level to simplify creation of tree
        current_level = min(size_list) # start at base
        asn_loopback_tree_node = None #keep track of to allocate loopbacks at end
        while True:
            cds = size_list[current_level]
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
            if len(ip_tree[current_level]) < 2:
                # Reached top of tree
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

        # Get loopback from loopback tree node
        loopback_hosts = asn_loopback_tree_node.subnet.iter_hosts()
        #router.loopback = loopback_hosts.next()
        for router in routers_by_asn[asn]:
            router.overlay.ip.loopback = loopback_hosts.next()

        # now allocate to the links of each cd
        for cd in asn_cds:
            hosts = cd.subnet.iter_hosts()
            for edge in cd.edges():
                edge.ip_address = hosts.next()

        # traverse tree, allocate back to loopbacks, and to nodes
        # TODO: should loopbacks be a sentinel type node for faster traversal rather than checking each time?


