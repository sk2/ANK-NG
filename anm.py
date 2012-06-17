import networkx as nx
from collections import namedtuple

class AutoNetkitException(Exception):
    pass

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
    def _phy_node(self):
# refer back to the physical node, to access attributes such as name
        return overlay_node(self.anm, "phy", self.node_id)

    def __repr__(self):
        #return "Overlay for %s in %s" % (self.node.fqdn, self.graph)
#TODO: label should come from node in physical graph
        #return self.anm.overlay.phy.device(self.node).label
        try:
            return self._phy_node.label
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
            return self._graph[self.node_id].get(key)
        except KeyError:
            raise IntegrityException(self.node_id)

    def __setattr__(self, key, val):
        """Sets node property
        This is useful for accesing attributes passed through from graphml"""
        self._graph[self.node][key] = val

class overlay_graph(namedtuple('overlay_graph', "anm, overlay_name")):
    """API to interact with an overlay graph in ANM"""
    __slots = ()

    def __repr__(self):
        return self.overlay_name

    @property
    def _graph(self):
        #access underlying graph for this overlay_node
        return self.anm._overlays[self.overlay_name]

    def __iter__(self):
        return iter(overlay_node(self.anm, self.overlay_name, node)
                for node in self._graph)

    def nodes(self):
        return self.__iter__()

    def __getattr__(self, key):
        print "ACCESS NODE IN GRAPH"
        """Access node in overlay graph"""
        print "trying to access key %s in overlay %s" % (key, self.overlay_name)
        if key in self._graph:
            return overlay_node(self.anm, self.overlay_name, key)
        else:
            raise DeviceNotFoundException("Unable to find ", key)

    def device(self, key):
        """To access programatically"""
        return overlay_node(self.anm, self.overlay_name, key)

    def __setattr__(self, key, val):
        """Set overlay graph
        TODO: do we want to restrict this? Ie import explicit function?
        """
        #self.node.network._graphs[self.graph].node[self.node][key] = val
        self.anm._g_overlays[key] = val

class overlay_accessor(namedtuple('overlay_accessor', "anm")):
    """API to access overlay graphs in ANM"""
    __slots = ()

    def __repr__(self):
        return "Available overlay graphs: %s" % ", ".join(sorted(self.anm._overlays.keys()))

    def __getattr__(self, key):
        """Access overlay graph"""
        return overlay_graph(self.anm, key)

    def __setattr__(self, key, val):
        """Set overlay graph
        TODO: do we want to restrict this? Ie import explicit function?
        """
        self.anm._overlays[key] = val

class AbstractNetworkModel(object):
    
    def __init__(self):
        self._overlays = {}
        self.add_overlay("phy")

    @property
    def _phy(self):
        return overlay_graph(self, "phy")

    def add_overlay(self, name, directed=False, multi_edge=False):
        """Adds overlay graph of name name"""
        graph = None
        if not directed and not multi_edge:
            graph = nx.Graph()
        elif directed and not multi_edge:
            graph = nx.DiGraph()
        elif not directed and multi_edge:
            graph = nx.MultiGraph()
        elif directed and not multi_edge:
            graph = nx.MultiDiGraph()

        self._overlays[name] = graph

    @property
    def overlay(self):
        return overlay_accessor(self)

    def devices(self, **kwargs):
        nodes = [n for n in self._phy]
        print "nodes are", list(nodes)
        nodes = self._phy.nodes() # All nodes in graph
        print "nodes are", list(nodes)

        # need to allow filter_func to access these args
        def filter_func(n):
            return all(self.graph.node[n].get(k) == v for k,v in
                            kwargs.items())

        return (n for n in nodes if filter_func(n))


    def group_by(self, nodes, **kwargs):
        """Groups nodes by argument, eg by asn, return as a dict... or as 
        itertools? can this be easily made into a dict?"""
        pass


def load_graphml(filename):
    graph = nx.read_graphml(filename)
# apply defaults
# relabel nodes
#other handling... split this into seperate module!
    return graph

def f_phy(G_in):
    return G_in


# probably want to create a graph from input with switches expanded to direct connections


"""TODO: allow graphs to be frozen for integrity, 
eg load input, freeze, 
and once done with overlays freeze them before nidb
"""

anm = AbstractNetworkModel()
G_in = load_graphml("multias.graphml")

anm.add_overlay("input")
anm.overlay.input = G_in
print anm.overlay.input
print list(anm.devices())

for device in anm.overlay.input:
    print device

G_phy = anm.overlay.phy
anm.add_overlay("ip")
anm.add_overlay("igp")
anm.add_overlay("bgp")
print anm.overlay

# call platform compiler to build NIDB

# pass to renderer


