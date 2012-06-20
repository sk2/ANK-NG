import networkx as nx
from collections import namedtuple
import pprint

class overlay_node_accessor(namedtuple('overlay_accessor', "nidb, node_id")):
    """API to access overlay nodes in ANM"""
#Used for consistency with ANM, where can also do node.overlay.graphics as well as node.graphics directly
    __slots = ()

    def __repr__(self):
        #TODO: make this list overlays the node is present in
        return "Overlay accessor for: %s" % self.nidb

    def __getattr__(self, key):
        """Access category"""
        return nidb_node_category(self.nidb, self.node_id, key)

class nidb_node_category(namedtuple('nidb_node_category', "nidb, node_id, category_id")):
    """API to access overlay graph node category in network"""
    __slots = ()

    def __repr__(self):
        return str(self._node_data.get(self.category_id))

    def __nonzero__(self):
        """Allows for accessing to set attributes
        This simplifies templates
        but also for easy check, eg if sw1.bgp can return False if category not set
        but can later do r1.bgp.attr = value
        """
        if self.category_id in self._node_data:
            return True
        return False

    @property
    def _node_data(self):
        return self.nidb._graph.node[self.node_id]

    def __getattr__(self, key):
        """Returns edge property"""
        return self._node_data[self.category_id].get(key)

    def __setattr__(self, key, val):
        """Sets edge property"""
        try:
            self._node_data[self.category_id][key] = val
        except KeyError:
            self._node_data[self.category_id] = {} # create dict for this data category
            setattr(self, key, val)

class nidb_node(namedtuple('nidb_node', "nidb, node_id")):
    """API to access overlay graph node in network"""
    __slots = ()

    def __repr__(self):
        return self._node_data['label']

    @property
    def _node_data(self):
        return self.nidb._graph.node[self.node_id]

    @property
    def label(self):
        return self.__repr__()

    def __getattr__(self, key):
        """Returns edge property"""
        return nidb_node_category(self.nidb, self.node_id, key)

    def __setattr__(self, key, val):
        """Sets edge property"""
        return nidb_node_category(self.nidb, self.node_id, key)

    @property
    def overlay(self):
        return overlay_node_accessor(self.nidb, self.node_id)

class nidb_graph_data(namedtuple('nidb_graph_data', "nidb")):
    __slots = ()

    def __repr__(self):
        return "NIDB data: %s" % self.nidb._graph.graph

    def __getattr__(self, key):
        """Returns edge property"""
        return self.nidb._graph.graph.get(key)

    def __setattr__(self, key, val):
        """Sets edge property"""
        self.nidb._graph.graph[key] = val



#TODO: make this inherit same overlay base as overlay_graph for add nodes etc properties
# but not the degree etc

class NIDB(object):

    def __init__(self):
        self._graph = nx.Graph() # only for connectivity, any other information stored on node

    def __repr__(self):
        return "nidb"

    def dump(self):
        return "%s %s %s" % (
                pprint.pformat(self._graph.graph),
                pprint.pformat(self._graph.nodes(data=True)),
                pprint.pformat(self._graph.edges(data=True))
                )



    @property
    def name(self):
        return self.__repr__()

    @property
    def data(self):
        return nidb_graph_data(self)

    def update(self, nbunch, **kwargs):
        for node in nbunch:
            for (category, key), value in kwargs.items():
                node.category.set(key, value)

    def add_nodes_from(self, nbunch, retain=[], **kwargs):
        if len(retain):
            add_nodes = []
            for n in nbunch:
                data = dict( (key, n.get(key)) for key in retain)
                add_nodes.append( (n.node_id, data) )
            nbunch = add_nodes
        else:
            nbunch = (n.node_id for n in nbunch) # only store the id in overlay
        self._graph.add_nodes_from(nbunch, **kwargs)

    def add_edge(self, src, dst, retain=[], **kwargs):
        self.add_edges_from([(src, dst)], retain, **kwargs)

    def add_edges_from(self, ebunch, retain=[], **kwargs):
        #TODO: need to test if given a (id, id) or an edge overlay pair... use try/except for speed
        try:
            if len(retain):
                add_edges = []
                for e in ebunch:
                    data = dict( (key, e.get(key)) for key in retain)
                    add_edges.append( (e.src.node_id, e.dst.node_id, data) )
                ebunch = add_edges
            else:
                ebunch = [(e.src.node_id, e.dst.node_id) for e in ebunch]
        except AttributeError:
            ebunch = [(src.node_id, dst.node_id) for src, dst in ebunch]

        #TODO: decide if want to allow nodes to be created when adding edge if not already in graph
        self._graph.add_edges_from(ebunch, **kwargs)

    def __iter__(self):
        return iter(nidb_node(self, node)
                for node in self._graph)



