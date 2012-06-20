import networkx as nx

class NIDB(object):

    def __init__(self):
        self._graph = nx.DiGraph() # directed to represent link data, initially just l3device -> switch


