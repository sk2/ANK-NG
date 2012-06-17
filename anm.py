import networkx as nx
from collections import namedtuple
import pprint

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

class overlay_graph(object):
    """API to interact with an overlay graph in ANM"""

    def __init__(self, anm, overlay_name):
        self._anm = anm
        self._overlay_name = overlay_name

    def __repr__(self):
        return self._overlay_name

    @property
    def _graph(self):
        #access underlying graph for this overlay_node
        return self._anm._overlays[self._overlay_name]

    def __iter__(self):
        return iter(overlay_node(self._anm, self._overlay_name, node)
                for node in self._graph)

    def nodes(self):
        return self.__iter__()

    def device(self, key):
        """To access programatically"""
        return overlay_node(self._anm, self._overlay_name, key)

    def filter(self, **kwargs):
        print "nodes in", self, "are", [n for n in self]

        # need to allow filter_func to access these args
        def filter_func(node):
            return all(node.key == val for key, val in
                            kwargs.items())

        return (n for n in self if filter_func(n))

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

    def group_by(self, nodes, **kwargs):
        """Groups nodes by argument, eg by asn, return as a dict... or as 
        itertools? can this be easily made into a dict?"""
        pass

    def devices(self, **kwargs):
        return self._phy.filter(**kwargs)

    def dump_graph(self, graph):
        print "Dumping graph", graph
        print "Nodes"
        print self.dump_nodes(graph)
        print "Edges"
        print self.dump_edges(graph)

    def dump_nodes(self, graph):
        debug_data = dict( (node, data)
                for node, data in sorted(self._overlays[graph].nodes(data=True)))
        return pprint.pformat(debug_data)

    def dump_edges(self, graph):
        debug_data = dict( ((src, dst), data
            ) for src, dst, data in sorted(self._overlays[graph].edges(data=True)))
        return pprint.pformat(debug_data)


def load_graphml(filename):
    graph = nx.read_graphml(filename)
# apply defaults
# relabel nodes
#other handling... split this into seperate module!
    return graph

# probably want to create a graph from input with switches expanded to direct connections

"""TODO: allow graphs to be frozen for integrity, 
eg load input, freeze, 
and once done with overlays freeze them before nidb
"""

anm = AbstractNetworkModel()
G_in = load_graphml("multias.graphml")

anm.add_overlay("input")
anm.overlay.input = G_in


print anm.dump_graph("input")

for device in anm.overlay.input:
    print device

G_phy = anm.overlay.phy

# build physical graph
print "devices are", [d for d in anm.overlay.input]
routers = [d for d in anm.overlay.input if d.device_type=="router"]
print "routers are", routers


print list(anm.devices())

anm.add_overlay("ip")
anm.add_overlay("igp")
anm.add_overlay("bgp")
print anm.overlay

# call platform compiler to build NIDB

# pass to renderer


