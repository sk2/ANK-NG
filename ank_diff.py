import networkx as nx
import glob
import os
import pprint

def diff_history(directory):
    glob_dir = os.path.join(directory, "*.pickle.tar.gz")
    pickle_files = glob.glob(glob_dir)
    pickle_files = sorted(pickle_files)
    pairs = [(a, b) for (a, b) in zip(pickle_files, pickle_files[1:])]
    for fileA, fileB in pairs:
        graphA = nx.read_gpickle(fileA)
        graphB = nx.read_gpickle(fileB)
        compare(graphA, graphB)


def dict_diff(dictA, dictB):
    """Calls self recursively to see if any changes
    If no changes returns None, if changes, returns changes
    If no keys in self, returns None"""
    #TODO: if no keys then return items???
    #print "comparing", dictA, dictB
    keysA = set(dictA.keys())
    keysB = set(dictB.keys())
    if keysA != keysB:
        print "keys added:", ", ".join(sorted(keysB - keysA))
        print "keys removed:", ", ".join(sorted(keysA - keysB))
    

def compare(graphA, graphB):
    diff = {}
    nodesA = set(graphA.nodes())
    nodesB = set(graphB.nodes())
    commonNodes = nodesA & nodesB

    diff['nodes'] = {
            'added': nodesB - nodesA,
            'removed': nodesA - nodesB,
            }

    for node in commonNodes:
        dictA = graphA.node[node]
        dictB = graphB.node[node]
        dict_diff(dictA, dictB)

    edgesA = set(graphA.edges())
    edgesB = set(graphB.edges())
    commonEdges = edgesA & edgesB
    diff['edges'] = {
            'added': edgesB - edgesA,
            'removed': edgesA - edgesB,
            }


    pprint.pprint(diff)

    
"""
want to return structure:
nodes {
    'added': []
    'removed': []
    'modified': {}
}
edges {
    'added': []
    'removed': []
    'modified': {}
}

and if modified, then list the properties
eg {
    'added': []
    'removed': []
    'modified': {}
}
and can be recursive
"""
