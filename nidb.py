import networkx as nx
from collections import namedtuple
import pprint


class overlay_data_dict(object):
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return str(self.data)

    def __getitem__(self, key):
        """To act as a dict eg self['item']"""
        return self.data.get(key)

    def __getattr__(self, key):
        """Access category"""
        return self.data.get(key)

class overlay_data_list_of_dicts(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return iter(overlay_data_dict(item) for item in self.data)


class overlay_node_accessor(object):
    def __init__(self, nidb, node_id):
#Set using this method to bypass __setattr__ 
        object.__setattr__(self, 'nidb', nidb)
        object.__setattr__(self, 'node_id', node_id)

    def __repr__(self):
        #TODO: make this list overlays the node is present in
        return "Overlay accessor for: %s" % self.nidb

    def __getattr__(self, key):
        """Access category"""
        return nidb_node_category(self.nidb, self.node_id, key)

class nidb_node_subcategory(object):
    def __init__(self, nidb, node_id, category_id, subcategory_id):
#Set using this method to bypass __setattr__ 
        object.__setattr__(self, 'nidb', nidb)
        object.__setattr__(self, 'node_id', node_id)
        object.__setattr__(self, 'category_id', category_id)
        object.__setattr__(self, 'subcategory_id', subcategory_id)

    @property
    def _data(self):
        return 

    def __repr__(self):
        return self.nidb._graph.node[self.node_id][self.category_id][self.subcategory_id]

class nidb_node_category(object):

    def __init__(self, nidb, node_id, category_id):
#Set using this method to bypass __setattr__ 
        object.__setattr__(self, 'nidb', nidb)
        object.__setattr__(self, 'node_id', node_id)
        object.__setattr__(self, 'category_id', category_id)

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
    def _category_data(self):
        return self._node_data[self.category_id]

    def __getitem__(self, key):
        """Used to access the data directly. calling node.key returns wrapped data for templates"""
        print "getting", key
        return self._category_data[key]

    @property
    def _node_data(self):
        return self.nidb._graph.node[self.node_id]

    def __getattr__(self, key):
        """Returns edge property"""
#TODO: allow appending if non existent: so can do node.bgp.session.append(data)
        data = self._category_data.get(key)
        try:
            [item.keys() for item in data]
            return overlay_data_list_of_dicts(data)
        except AttributeError:
            pass # not a dict
        except TypeError:
            pass # also not a dict
        print "returning", type(data), data
        return data

    def dump(self):
        return str(self._node_data)

# check if list

    def __setattr__(self, key, val):
        """Sets edge property"""
        try:
            self._node_data[self.category_id][key] = val
        except KeyError:
            self._node_data[self.category_id] = {} # create dict for this data category
            setattr(self, key, val)


class nidb_node(object):
    """API to access overlay graph node in network"""

    def __init__(self, nidb, node_id):
#Set using this method to bypass __setattr__ 
        object.__setattr__(self, 'nidb', nidb)
        object.__setattr__(self, 'node_id', node_id)

    def __repr__(self):
        return self._node_data['label']

    @property
    def _node_data(self):
        return self.nidb._graph.node[self.node_id]

    def dump(self):
        return str(self._node_data)

    @property
    def id(self):
        return self.node_id

    @property
    def label(self):
        return self.__repr__()

    def __getattr__(self, key):
        """Returns edge property"""
        data = self._node_data.get(key)
        try:
            [item.keys() for item in data]
            return overlay_data_list_of_dicts(data)
        except TypeError:
            pass # Not set yet
        except AttributeError:
            pass # not a dict

        try:
            data.keys() 
            return nidb_node_category(self.nidb, self.node_id, key)
        except TypeError:
            pass # Not set yet
        except AttributeError:
            pass # not a dict

        if data:
            return data
        else:
            return nidb_node_category(self.nidb, self.node_id, key)

    def __setattr__(self, key, val):
        """Sets edge property"""
        self._node_data[key] = val
        #return nidb_node_category(self.nidb, self.node_id, key)

    @property
    def overlay(self):
        return overlay_node_accessor(self.nidb, self.node_id)

class nidb_graph_data(object):
    """API to access overlay graph node in network"""

    def __init__(self, nidb, node_id):
#Set using this method to bypass __setattr__ 
        object.__setattr__(self, 'nidb', nidb)

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

class NIDB_base(object):

    #TODO: inherit common methods from same base as overlay

    def __init__(self):
        pass

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

    def __len__(self):
        return len(self._graph)

    def node(self, key):
        """Returns node based on name
        This is currently O(N). Could use a lookup table"""
#TODO: check if node.node_id in graph, if so return wrapped node for this...
# returns node based on name
        try:
            if key.node_id in self._graph:
                return nidb_node(self, key.node_id)
        except AttributeError:
            # doesn't have node_id, likely a label string, search based on this label
            for node in self:
                if str(node) == key:
                    return node
            print "Unable to find node", key, "in", self
            return None

    @property
    def data(self):
        return nidb_graph_data(self)

    def update(self, nbunch, **kwargs):
        for node in nbunch:
            for (category, key), value in kwargs.items():
                node.category.set(key, value)

    def nodes(self, *args, **kwargs):
        result = self.__iter__()
        if len(args) or len(kwargs):
            result = self.filter(result, *args, **kwargs)
        return result

    def filter(self, nbunch = None, *args, **kwargs):
        #TODO: also allow nbunch to be passed in to subfilter on...?
        """TODO: expand this to allow args also, ie to test if value evaluates to True"""
        # need to allow filter_func to access these args
        print "filtering", args, kwargs.items()
        for node in nbunch:
            print type(node.platform)
            print node.platform == 'ios'
        if not nbunch:
            nbunch = self.nodes()
        def filter_func(node):
            return (
                    all(getattr(node, key) for key in args) and
                    all(getattr(node, key) == val for key, val in kwargs.items())
                    )

        return (n for n in nbunch if filter_func(n))

    def add_nodes_from(self, nbunch, retain=[], **kwargs):
        try:
            retain.lower()
            retain = [retain] # was a string, put into list
        except AttributeError:
            pass # already a list

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
        try:
            retain.lower()
            retain = [retain] # was a string, put into list
        except AttributeError:
            pass # already a list

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

class NIDB(NIDB_base):
    def __init__(self):
        self._graph = nx.Graph() # only for connectivity, any other information stored on node

    def subgraph(self, nbunch, name = None):
        nbunch = (n.node_id for n in nbunch) # only store the id in overlay
        return overlay_subgraph(self._graph.subgraph(nbunch), name)

class overlay_subgraph(NIDB_base):
    def __init__(self, graph, name = None):
        self._graph = graph # only for connectivity, any other information stored on node
        print graph
        self._name = name
    
