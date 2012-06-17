import networkx as nx
from collections import namedtuple
import itertools
import pprint

#TODO: add helper functions such as router, ie ank.router(device): return device.overlay.phys.device_type == "router"

#Add plotting abilities, and allow legend attribute to be set: for both color and symbol

# working with views allows us to spin off subgraphs, and work with them the same as a standard overlay

class AutoNetkitException(Exception):
    pass

class OverlayNotFound(AutoNetkitException):
    def __init__(self, Errors):
        self.Errors = Errors

    def __str__(self):
        return "Overlay %s not found" % self.Errors

class IntegrityException(AutoNetkitException):
    def __init__(self, Errors):
        self.Errors = Errors

    def __str__(self):
        return "Device %s not found in physical graph" % self.Errors

class DeviceNotFoundException(AutoNetkitException):
    def __init__(self, message, Errors):
        Exception.__init__(self, message)
        self.Errors = Errors

    def __str__(self):
        return "Unable to find %s" % self.Errors

class overlay_node_accessor(namedtuple('overlay_accessor', "anm, node_id")):
    """API to access overlay nodes in ANM"""
    __slots = ()

    def __repr__(self):
        #TODO: make this list overlays the node is present in
        return "Overlay graphs: %s" % ", ".join(sorted(self.anm._overlays.keys()))

    def __getattr__(self, key):
        """Access overlay graph"""
        return overlay_node(self.anm, key, self.node_id)

class overlay_node(namedtuple('node', "anm, overlay_id, node_id")):
    """API to access overlay graph node in network"""
    __slots = ()

#TODO: allow access back up to overlays from this
# eg self.ip.property self.bgp.property etc

    @property
    def _graph(self):
        """Return graph the node belongs to"""
        return self.anm._overlays[self.overlay_id]

    @property
    def id(self):
        return self.node_id

    @property
    def _phy_node(self):
# refer back to the physical node, to access attributes such as name
        return overlay_node(self.anm, "phy", self.node_id)

    @property
    def data(self):
        return self._graph.node[self.node_id].keys()

    @property
    def overlay(self):
        """Access node in another overlay graph"""
        return overlay_node_accessor(self.anm, self.node_id)
        

    def __repr__(self):
        #return "Overlay for %s in %s" % (self.node.fqdn, self.graph)
#TODO: label should come from node in physical graph
        #return self.anm.overlay.phy.device(self.node).label
        try:
            return self.overlay.phy.label
        except IntegrityException:
# Node not in physical graph
            try:
                return self._graph.node[self.node_id]['label']
            except KeyError:
                return self.node_id # No label set for this node, return node id

    def __getattr__(self, key):
        """Returns node property
        This is useful for accesing attributes passed through from graphml"""
#TODO: make this log to debug on a miss, ie if key not found: do a try/except for KeyError for this
        try:
            return self._graph.node[self.node_id].get(key)
        except KeyError:
            raise IntegrityException(self.node_id)

    def get(self, key):
        """For consistency, node.get(key) is neater than getattr(node, key)"""
        return self.__getattr__(key)

    def __setattr__(self, key, val):
        """Sets node property
        This is useful for accesing attributes passed through from graphml"""
        self._graph[self.node][key] = val

class overlay_edge(namedtuple('link', "anm, overlay_name, src_id, dst_id")):
    """API to access link in network"""
    __slots = ()
    def __repr__(self):
        return "(%s, %s)" % (self.src, self.dst)

    @property
    def src(self):
        return overlay_node(self.anm, self.overlay_name, self.src_id)

    @property
    def dst(self):
        return overlay_node(self.anm, self.overlay_name, self.dst_id)

    @property
    def data(self):
        return self._graph[self.src_id][self.dst_id].keys()

    @property
    def _graph(self):
        """Return graph the node belongs to"""
        return self.anm._overlays[self.overlay_name]

    def get(self, key):
        """For consistency, edge.get(key) is neater than getattr(edge, key)"""
        return self.__getattr__(key)

    def __getattr__(self, key):
        """Returns edge property"""
        return self._graph[self.src_id][self.dst_id].get(key)

    def __setattr__(self, key, val):
        """Sets edge property"""
        self._graph[self.src_id][self.dst_id][key] = val

class OverlayBase(object):
    """Base class for overlays - overlay graphs, subgraphs, projections, etc"""

    def __init__(self, anm, overlay_name):
        if overlay_name not in anm._overlays:
            raise OverlayNotFound(overlay_name)
        self._anm = anm
        self._overlay_name = overlay_name

    def __repr__(self):
        return self._overlay_name

    def __contains__(self, n):
        return n.node_id in self._graph

#TODO: Allow overlay data to be set/get, ie graph.graph eg for asn subnet allocations

    @property
    def name(self):
        return self._overlay_name

    def dump(self):
        #TODO: map this to ank functions
        self._anm.dump_graph(self)

    def has_edge(self, edge):
        """Tests if edge in graph"""
#TODO: handle case of user creating edge, eg test tuples and ids directly
        return self._graph.has_edge(edge.src, edge.dst)



    def __iter__(self):
        return iter(overlay_node(self._anm, self._overlay_name, node)
                for node in self._graph)

    def nodes(self):
        return self.__iter__()

    def device(self, key):
        """To access programatically"""
        return overlay_node(self._anm, self._overlay_name, key)

    def groupby(self, attribute):
        """Returns a dictionary sorted by attribute
        
        >>> G_in.groupby("asn")
        {u'1': [r1, r2, r3, sw1], u'2': [r4]}
        """
        result={}

        data = self.nodes()
        data = sorted(data, key= lambda x: x.get(attribute))
        for k, g in itertools.groupby(data, key= lambda x: x.get(attribute)):
            result[k] = list(g)
        return result

    def filter(self, **kwargs):
        # need to allow filter_func to access these args
        def filter_func(node):
            return all(node.get(key) == val for key, val in
                            kwargs.items())

        return (n for n in self if filter_func(n))

    def edges(self, nbunch = None):
        if nbunch:
            nbunch = (n.node_id for n in nbunch) # only store the id in overlay
        return iter(overlay_edge(self._anm, self._overlay_name, src, dst)
                for src, dst in self._graph.edges(nbunch))

class overlay_subgraph(OverlayBase):

    def __init__(self, anm, overlay_name, graph):
        super(overlay_subgraph, self).__init__(anm, overlay_name)
        self._graph = graph



class overlay_graph(OverlayBase):
    """API to interact with an overlay graph in ANM"""

    @property
    def _graph(self):
        #access underlying graph for this overlay_node
        return self._anm._overlays[self._overlay_name]

    # these work similar to their nx counterparts: just need to strip the node_id
    def add_nodes_from(self, nbunch, retain=[], default={}):
        if len(retain):
            add_nodes = []
            for n in nbunch:
                data = dict( (key, n.get(key)) for key in retain)
                add_nodes.append( (n.node_id, data) )
            nbunch = add_nodes
        else:
            nbunch = (n.node_id for n in nbunch) # only store the id in overlay
        self._graph.add_nodes_from(nbunch, **default)

    def add_edges_from(self, ebunch, retain=[], default={}):
        #TODO: need to test if given a (id, id) or an edge overlay pair... use try/except for speed
        if len(retain):
            add_edges = []
            for e in ebunch:
                data = dict( (key, e.get(key)) for key in retain)
                add_edges.append( (e.src.node_id, e.dst.node_id, data) )
            ebunch = add_edges
        else:
            ebunch = ((e.src.node_id, e.dst.node_id) for e in ebunch) # only store the id in overlay
        ebunch = list(ebunch)
        print "ebunch", ebunch
        self._graph.add_edges_from(ebunch, **default)

    def subgraph(self, nbunch):
        return overlay_subgraph(self._anm, self._overlay_name, self._graph.subgraph(nbunch))

class overlay_accessor(namedtuple('overlay_accessor', "anm")):
    """API to access overlay graphs in ANM"""
    __slots = ()

    def __repr__(self):
        return "Available overlay graphs: %s" % ", ".join(sorted(self.anm._overlays.keys()))

    def __getattr__(self, key):
        """Access overlay graph"""
        return overlay_graph(self.anm, key)

class AbstractNetworkModel(object):
    
    def __init__(self):
        self._overlays = {}
        self.add_overlay("phy")

    @property
    def _phy(self):
        return overlay_graph(self, "phy")

    def add_overlay(self, name, graph = None, directed=False, multi_edge=False):
        """Adds overlay graph of name name"""
        if graph:
            pass
        elif not directed and not multi_edge:
            graph = nx.Graph()
        elif directed and not multi_edge:
            graph = nx.DiGraph()
        elif not directed and multi_edge:
            graph = nx.MultiGraph()
        elif directed and not multi_edge:
            graph = nx.MultiDiGraph()

        self._overlays[name] = graph
        return overlay_graph(self, name)

    @property
    def overlay(self):
        return overlay_accessor(self)

    def devices(self, **kwargs):
        return self._phy.filter(**kwargs)

    def node_label(self, node):
        """Returns node label from physical graph"""
        return overlay_node(self, "phy", node).label

    #TODO: move this out into debug module
    def dump_graph(self, graph):
        print "Dumping graph '%s'" % graph
        print "Graph"
        print self.dump_graph_data(graph)
        print "Nodes"
        print self.dump_nodes(graph)
        print "Edges"
        print self.dump_edges(graph)

    def dump_graph_data(self, graph):
        debug_data = dict( (key, val)
                for key, val in sorted(graph._graph.graph.items()))
        return pprint.pformat(debug_data)

    def dump_nodes(self, graph):
        debug_data = dict( (node, data)
                for node, data in sorted(graph._graph.nodes(data=True)))
        return pprint.pformat(debug_data)

    def dump_edges(self, graph):
        debug_data = dict( ((src, dst), data
            ) for src, dst, data in sorted(graph._graph.edges(data=True)))
        return pprint.pformat(debug_data)

def load_graphml(filename):
    graph = nx.read_graphml(filename)
#TODO: node labels if not set, need to set from a sequence, ensure unique... etc

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

    # and ensure asn is integer
    for node in graph:
        graph.node[node]['asn'] = int(graph.node[node]['asn'])

    ank_edge_defaults = {
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
        ids, x, y = zip(*[(node.id , node.overlay.input.x, node.overlay.input.y)
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
    
    """
    TODO: fix this
    if edge_label_attribute:
        print "get ttpe", [edge.get(edge_label_attribute) for edge in overlay_graph.edges()]
        edge_labels = dict ( ( (edge.src.node_id, edge.dst.node_id), edge.get(edge_label_attribute))
            for edge in overlay_graph.edges())
        print "get ttpe", [edge.get(edge_label_attribute) for edge in overlay_graph.edges()]
        print "edge labels", edge_labels
        nx.draw_networkx_edge_labels(graph, pos, 
                            labels=edge_labels,
                            font_size = 12,
                            font_color = font_color)

        """


#TODO: where is anm from here? global? :/
    labels = dict( (n, anm.node_label(n)) for n in graph)
    nx.draw_networkx_labels(graph, pos, 
                            labels=labels,
                            font_size = 12,
                            font_color = font_color)

    if show:
        plt.show()
    if save:
        filename = "%s.pdf" % graph_name
        plt.savefig(filename)

    plt.close()

# probably want to create a graph from input with switches expanded to direct connections

"""TODO: allow graphs to be frozen for integrity, 
eg load input, freeze, 
and once done with overlays freeze them before nidb
"""

anm = AbstractNetworkModel()
input_graph = load_graphml("example.graphml")

G_in = anm.add_overlay("input", input_graph)

#G_phy created automatically by ank
G_phy = anm.overlay.phy

#print "grouped by", anm.overlay.input.groupby("device_type")
#print "grouped by", anm.overlay.input.groupby("asn")

# build physical graph
routers = [d for d in G_in if d.device_type=="router"]
#routers = G_in.filter(device_type='router')

G_phy.add_nodes_from(routers, retain=['label', 'device_type'], default={'color': 'red'})

#print list(anm.devices())

G_ip = anm.add_overlay("ip")
G_igp = anm.add_overlay("igp")
G_bgp = anm.add_overlay("bgp")
print anm.overlay

print "devices in phy", [n for n in G_phy]

edges = [edge.data for edge in G_in.edges()]
print edges

G_bgp.add_nodes_from([d for d in G_in if d.device_type == "router"])

present_nodes = [n for n in G_in if n in G_bgp and n.asn == 1]
print "present nodes", present_nodes


#TODO: need to be able to create overlay subgraphs, that inherit from same base, but have _graph stored internally
# ie properties are not stored, they are just a view...

ebgp_edges = [edge for edge in G_in.edges() if edge.src.asn != edge.dst.asn]
G_bgp.add_edges_from(ebgp_edges, default={'type:': 'ebgp'})
# now iBGP
for asn, devices in G_in.groupby("asn").items():
    print "iBGP for asn", asn

    asn_subgraph = G_in.subgraph(devices)
    print "subgraph edges", list(asn_subgraph.edges())
    for edge in asn_subgraph.edges():
        print "asn subgraph has edge", edge

    routers = [d for d in devices if d.device_type == "router"]
    print "routers are", routers
    print "g in edges", list(G_in.edges(routers))
    ibgp_edges = [ edge for edge in G_in.edges(routers)]
    print "ibgp edges", ibgp_edges
    #G_bgp.add_edges_from(ibgp_edges, default={'type:': 'ibgp'})
    
# full iBGP mesh


G_bgp.dump()
plot(G_bgp, edge_label_attribute="type")

# call platform compiler to build NIDB
# NIDB copies properties from each graph, including links, but also allows extra details to be added.
# Does this by creating a dict for each copied in type, and an edge with edge type


# pass each NIDB to renderer


# Render: NIDB has a property for topology creation, which is also a folder or a mako template, same as for devices.
