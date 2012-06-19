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
    def is_router(self):
        return self.phy.device_type == "router"

    @property
    def is_switch(self):
        return self.phy.device_type == "switch"

    @property
    def is_server(self):
        return self.phy.device_type == "server"

#TODO: Add other base device_types

    @property
    def id(self):
        return self.node_id

    def degree(self):
        return self._graph.degree(self.node_id)

    @property
    def label(self):
        return self.__repr__()

    @property
    def phy(self):
        """Shortcut back to physical overlay_node
        Same as node.overlay.phy
        ie node.phy.x is same as node.overlay.phy.x
        """
# refer back to the physical node, to access attributes such as name
        return overlay_node(self.anm, "phy", self.node_id)

    @property
    def data(self):
        return self._graph.node[self.node_id].keys()

    @property
    def overlay(self):
        """Access node in another overlay graph"""
        return overlay_node_accessor(self.anm, self.node_id)

    def edges(self):
        #TODO: want to add filter for *args and **kwargs here too
        return iter(overlay_edge(self.anm, self.overlay_id, src, dst)
                for src, dst in self._graph.edges(self.node_id))

        
    def __repr__(self):
        """Try label if set in overlay, otherwise from physical, otherwise node id"""
        label = self._graph.node[self.node_id].get("label")
        if not label:
            try:
                label =  self.phy.label
            except IntegrityException:
                label = self.node_id # node not in physical graph
            except KeyError:
                label = self.node_id # node not in physical graph

        return label

    def __getattr__(self, key):
        """Returns node property
        This is useful for accesing attributes passed through from graphml"""
#TODO: make this log to debug on a miss, ie if key not found: do a try/except for KeyError for this
        try:
            return self._graph.node[self.node_id].get(key)
        except KeyError:
            return

    def get(self, key):
        """For consistency, node.get(key) is neater than getattr(node, key)"""
        return self.__getattr__(key)

    def __setattr__(self, key, val):
        """Sets node property
        This is useful for accesing attributes passed through from graphml"""
        try:
            self._graph.node[self.node_id][key] = val
        except KeyError:
            self._graph.add_node(self.node_id)
            self.set(key, val)

    def set(self, key, val):
        """For consistency, node.set(key, value) is neater than setattr(node, key, value)"""
        return self.__setattr__(key, val)

class overlay_edge(namedtuple('link', "anm, overlay_id, src_id, dst_id")):
    """API to access link in network"""
    __slots = ()
    def __repr__(self):
        return "(%s, %s)" % (self.src, self.dst)

    @property
    def src(self):
        return overlay_node(self.anm, self.overlay_id, self.src_id)

    @property
    def dst(self):
        return overlay_node(self.anm, self.overlay_id, self.dst_id)

    @property
    def data(self):
        return self._graph[self.src_id][self.dst_id].keys()

    @property
    def _graph(self):
        """Return graph the node belongs to"""
        return self.anm._overlays[self.overlay_id]

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

    def __init__(self, anm, overlay_id):
        if overlay_id not in anm._overlays:
            raise OverlayNotFound(overlay_id)
        self._anm = anm
        self._overlay_id = overlay_id

    def __repr__(self):
        return self._overlay_id

    def __contains__(self, n):
        return n.node_id in self._graph

    def node(self, key):
        """Returns node based on name
        This is currently O(N). Could use a lookup table"""
#TODO: check if node.node_id in graph, if so return wrapped node for this...
# returns node based on name
        for node in self:
            if str(node) == key:
                return node
        print "Unable to find node", key, "in", self
        return None

#TODO: Allow overlay data to be set/get, ie graph.graph eg for asn subnet allocations

    def degree(self, node):
        return node.degree()

    def neighbors(self, node):
        iter(overlay_node(self._anm, self._overlay_id, node)
                for node in self._graph.neighbors(node.node_id))

    @property
    def overlay(self):
        """Get to other overlay graphs in functions"""
        return overlay_accessor(self._anm)

    @property
    def name(self):
        return self.__repr__()

    def node_label(self, node):
        return repr(overlay_node(self._anm, self._overlay_id, node))

    def dump(self):
        #TODO: map this to ank functions
        self._anm.dump_graph(self)

    def has_edge(self, edge):
        """Tests if edge in graph"""
#TODO: handle case of user creating edge, eg test tuples and ids directly
        return self._graph.has_edge(edge.src, edge.dst)

    def __iter__(self):
        return iter(overlay_node(self._anm, self._overlay_id, node)
                for node in self._graph)

    def __len__(self):
        return len(self._graph)

    def nodes(self, *args, **kwargs):
        result = self.__iter__()
        if len(args) or len(kwargs):
            result = self.filter(result, *args, **kwargs)
        return result

    def device(self, key):
        """To access programatically"""
        return overlay_node(self._anm, self._overlay_id, key)

    def groupby(self, attribute, nodes = None):
        """Returns a dictionary sorted by attribute
#TODO: Also want to be able to return list of subgraphs based on groupby, eg per ASN subgraphs
        
        >>> G_in.groupby("asn")
        {u'1': [r1, r2, r3, sw1], u'2': [r4]}
        """
        result={}
    
        if not nodes:
            data = self.nodes()
        else:
            data = nodes
        data = sorted(data, key= lambda x: x.get(attribute))
        for k, g in itertools.groupby(data, key= lambda x: x.get(attribute)):
            result[k] = list(g)

        #TODO: should this return .items() to be consistent with other iterables?
        return result

    def filter(self, nbunch = None, *args, **kwargs):
        #TODO: also allow nbunch to be passed in to subfilter on...?
        """TODO: expand this to allow args also, ie to test if value evaluates to True"""
        # need to allow filter_func to access these args
        if not nbunch:
            nbunch = self.nodes()
        def filter_func(node):
            return (
                    all(node.get(key) for key in args) and
                    all(node.get(key) == val for key, val in kwargs.items())
                    )

        return (n for n in nbunch if filter_func(n))

    def edges(self, nbunch = None, *args, **kwargs):
# nbunch may be single node
        if nbunch:
            try:
                nbunch = nbunch.node_id
            except AttributeError:
                nbunch = (n.node_id for n in nbunch) # only store the id in overlay
        return iter(overlay_edge(self._anm, self._overlay_id, src, dst)
                for src, dst in self._graph.edges(nbunch))

class overlay_subgraph(OverlayBase):

    def __init__(self, anm, overlay_id, graph, name = None):
        super(overlay_subgraph, self).__init__(anm, overlay_id)
        self._graph = graph
        self._subgraph_name = name

    def __repr__(self):
        return self._subgraph_name


class overlay_graph(OverlayBase):
    """API to interact with an overlay graph in ANM"""
#TODO: provide an strip_id function to turn node tuples back into just ids for the graph

    @property
    def _graph(self):
        #access underlying graph for this overlay_node
        return self._anm._overlays[self._overlay_id]

    # these work similar to their nx counterparts: just need to strip the node_id
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

    def update(self, nbunch, **kwargs):
        """Sets property defined in kwargs to all nodes in nbunch"""
        for node in nbunch:
            for key, value in kwargs.items():
                node.set(key, value)

    def subgraph(self, nbunch, name=None):
        nbunch = (n.node_id for n in nbunch) # only store the id in overlay
        return overlay_subgraph(self._anm, self._overlay_id, self._graph.subgraph(nbunch), name)

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

    def devices(self, *args, **kwargs):
        return self._phy.filter(*args, **kwargs)

    def node_label(self, node):
        """Returns node label from physical graph"""
        try:
            return overlay_node(self, "phy", node).label
        except IntegrityException:
            return node # not in physical graph

    #TODO: move this out into debug module
    def dump_graph(self, graph):
        print "----Graph %s----" % graph
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
        debug_data = dict( (graph.node_label(node), data)
                for node, data in (graph._graph.nodes(data=True)))
        return pprint.pformat(debug_data)

    def dump_edges(self, graph):
        debug_data = dict( ((graph.node_label(src), graph.node_label(dst)), data
            ) for src, dst, data in (graph._graph.edges(data=True)))
        return pprint.pformat(debug_data)



"""TODO: allow graphs to be frozen for integrity, 
eg load input, freeze, 
and once done with overlays freeze them before nidb
"""


