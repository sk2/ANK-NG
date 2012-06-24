import networkx as nx
import glob
import os
import pprint
from collections import defaultdict

def diff_history(directory):
    glob_dir = os.path.join(directory, "*.pickle.tar.gz")
    pickle_files = glob.glob(glob_dir)
    pickle_files = sorted(pickle_files)
    pairs = [(a, b) for (a, b) in zip(pickle_files, pickle_files[1:])]
    for fileA, fileB in pairs:
        graphA = nx.read_gpickle(fileA)
        graphB = nx.read_gpickle(fileB)
        compare(graphA, graphB)

def element_diff(elemA, elemB):
    try:
        if len(elemA) > 1 and len(elemB) > 1:
            list_diff(elemA, elemB)
    except TypeError:
        pass
    if elemA != elemB:
        return { 'before': elemA, 'after': elemB, }

def list_diff(listA, listB):
    listA = sorted(listA)
    listB = sorted(listB)
    elements = zip(listA, listB)
    list_changed = []
    for (elemA, elemB) in elements:
        try:
            elemA.keys() # see if both are dicts
            elemB.keys()
            elem_changed = dict_diff(elemA, elemB) # are dicts, compare as a dict
            if elem_changed:
                list_changed.append(elem_changed)
        except AttributeError:
            try:
                if len(elemA) > 1 and len(elemB) > 1:
                    return list_diff(elemA, elemB)
            except AttributeError:
                return element_diff(elemA, elemB)

    if list_changed:
        return list_changed



def dict_diff(dictA, dictB):
    """Calls self recursively to see if any changes
    If no changes returns None, if changes, returns changes
    If no keys in self, returns None"""
    #TODO: if no keys then return items???
    #print "comparing", dictA, dictB
    diff = defaultdict(dict)
    try:
        keysA = set(dictA.keys())
        keysB = set(dictB.keys())
    except AttributeError:
# if list, compare list items
        modified = element_diff(dictA, dictB)
        if modified:
            print modified
        return


#TODO: change commonKeys to common_keys

    commonKeys = keysA & keysB
    keys_modified = {}
    for key in commonKeys:
        subDictA = dictA[key]
        subDictB = dictB[key]
        changed = dict_diff(subDictA, subDictB)
        if changed:
            keys_modified[key] = changed

    keys_added = keysB - keysA
    if keys_added:
        diff['added'] = keys_added
    keys_removed = keysA - keysB
    if keys_removed:
        diff['removed'] = keys_removed
    if keys_modified:
        diff['modified'] = keys_modified

    if diff:
        #return dict(diff)
        pass

def compare(graphA, graphB):
    diff = {}
    nodesA = set(graphA.nodes())
    nodesB = set(graphB.nodes())
    commonNodes = nodesA & nodesB
    diff = defaultdict(dict)
    #diff['nodes'] = {
            #'added': nodesB - nodesA,
            #'removed': nodesA - nodesB,
            #}

    for node in commonNodes:
        dictA = graphA.node[node]
        dictB = graphB.node[node]
        node_diff = dict_diff(dictA, dictB)
        print "changed nodes"
        pprint.pprint(node_diff)

    edgesA = set(graphA.edges())
    edgesB = set(graphB.edges())
    commonEdges = edgesA & edgesB
    added_edges = edgesB - edgesA
    if added_edges:
        diff['edges']['added'] = added_edges
    removed_edges = edgesA - edgesB
    if removed_edges:
        diff['edges']['removed'] = removed_edges

    for (src, dst) in commonEdges:
        dictA = graphA[src][dst]
        dictB = graphB[src][dst]
        dict_diff(dictA, dictB)


    #pprint.pprint(diff)


    
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
