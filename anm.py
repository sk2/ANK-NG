import networkx as nx
from collections import namedtuple

class DeviceNotFoundException(Exception):
       def __init__(self, message):
        Exception.__init__(self, message)

class overlay_node(namedtuple('node', "anm, overlay_graph, node")):
    """API to access overlay graph node in network"""
    __slots = ()

    @property
    def _graph(self):
        """Return graph the node belongs to"""
        return self.anm._overlays[self.overlay_graph]

    def __repr__(self):
        #return "Overlay for %s in %s" % (self.node.fqdn, self.graph)
#TODO: label should come from node in physical graph
        return self.anm.overlay.phy.device(self.node).label

    def __getattr__(self, key):
        """Returns node property
        This is useful for accesing attributes passed through from graphml"""
#TODO: make this log to debug on a miss, ie if key not found: do a try/except for KeyError for this
        try:
            return self._graph[self.node].get(key)
            pass
        except KeyError:
            raise DeviceNotFoundException

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
        return iter(overlay_node(self.anm, self.overlay_graph, node)
                for node in self._graph)

    def __getattr__(self, key):
        """Access node in overlay graph"""
        if key in self._graph:
            return overlay_node(self.anm, self.overlay_name, key)
        else:
            raise DeviceNotFoundException("Unable to find %s" % key)

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

    #    """Set overlay graph
    #    TODO: do we want to restrict this? Ie import explicit function?
    #    """
    #    #self.node.network._graphs[self.graph].node[self.node][key] = val
    #    self.anm._g_overlays[key] = val

class AbstractNetworkModel(object):
    
    def __init__(self):
        self._overlays = {}
        self.add_overlay("phy")

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

def load_graphml(filename):
    graph = nx.read_graphml(filename)
# apply defaults
# relabel nodes
#other handling... split this into seperate module!
    return graph

def f_phy(G_in):
    return G_in

anm = AbstractNetworkModel()
G_in = load_graphml("multias.graphml")

anm.add_overlay("input")
anm.overlay.input = G_in
print anm.overlay.input

for device in anm.overlay.input:
    print device

G_phy = anm.overlay.phy
anm.add_overlay("ip")
anm.add_overlay("igp")
anm.add_overlay("bgp")
print anm.overlay
