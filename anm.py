import networkx as nx
from collections import namedtuple


class overlay_node(namedtuple('node', "anm, overlay_graph, node")):
    """API to access overlay graph node in network"""
    __slots = ()

    def __repr__(self):
        #return "Overlay for %s in %s" % (self.node.fqdn, self.graph)
#TODO: label should come from node in physical graph
        print "AAAAAA"
        pass

    def __getattr__(self, key):
        """Returns node property
        This is useful for accesing attributes passed through from graphml"""
#TODO: make this log to debug on a miss, ie if key not found: do a try/except for KeyError for this
        try:
            return self.anm._g_overlays[self.overlay_graph][self.node].get(key)
        except KeyError:
            #LOG.warn("Node %s not present in overlay graph %s" % (self.node, self.graph))
            print "Node not present"

    def __setattr__(self, key, val):
        """Sets node property
        This is useful for accesing attributes passed through from graphml"""
        self.anm._g_overlays[self.overlay_graph][self.node][key] = val

class overlay_graph(namedtuple('overlay_graph', "anm, overlay_name")):
    """API to interact with an overlay graph in ANM"""
    __slots = ()

    def __repr__(self):
        return "AA"

    def __iter__(self):
        return self
        return iter(self.anm._g_overlays[self.name])

    def __getattr__(self, key):
        """Access node in overlay graph"""
        return self.anm._g_overlays[self.name][key]

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
        return "Available overlay graphs: %s" % ", ".join(sorted(self.anm._g_overlays.keys()))

    def __getattr__(self, key):
        """Access overlay graph"""
        return self.anm._g_overlays[key]

    def __setattr__(self, key, val):
        """Set overlay graph
        TODO: do we want to restrict this? Ie import explicit function?
        """
        #self.node.network._graphs[self.graph].node[self.node][key] = val
        self.anm._g_overlays[key] = val

class AbstractNetworkModel(object):
    
    def __init__(self):
        self._g_overlays = {}

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

        self._g_overlays[name] = graph

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


anm.add_overlay("phy")
G_phy = anm.overlay.phy
anm.add_overlay("ip")
anm.add_overlay("igp")
anm.add_overlay("bgp")
print anm.overlay

print anm._g_overlays
