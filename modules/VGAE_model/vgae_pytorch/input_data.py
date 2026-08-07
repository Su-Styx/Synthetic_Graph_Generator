'''
****************NOTE*****************
CREDITS : Thomas Kipf
since datasets are the same as those in kipf's implementation, 
Their preprocessing source was used as-is.
*************************************
'''
import numpy as np
import sys
import pickle as pkl
import networkx as nx
import scipy.sparse as sp

# my own import 
import pandas as pd

def parse_index_file(filename):
    index = []
    for line in open(filename):
        index.append(int(line.strip()))
    return index


def load_data(dataset, edges_path=None, nodes_path=None):
    print("reading edges", flush=True)
    g = pd.read_csv(edges_path)
    print("edges shape", g.shape, "columns", list(g.columns), flush=True)

    print("reading nodes", flush=True)
    n = pd.read_csv(nodes_path)
    print("nodes shape", n.shape, "columns", list(n.columns), flush=True)

    print("sorting nodes", flush=True)
    n = n.sort_values("node_index").reset_index(drop=True)

    print("building graph", flush=True)
    G = nx.from_pandas_edgelist(g, source="x_index", target="y_index")
    print("graph built", G.number_of_nodes(), G.number_of_edges(), flush=True)

    print("building adjacency", flush=True)
    adj = nx.adjacency_matrix(G, nodelist=n["node_index"].tolist())
    print("adjacency built", adj.shape, flush=True)

    print("building features", flush=True)
    type_features = pd.get_dummies(n["node_type"], prefix="type", dtype=np.int8)
    features = type_features.to_numpy(dtype=np.float32)
    print("features built", features.shape, flush=True)
        # if statement my own for testin
    if dataset == 'disease_features':

        # edges_path = edges_path or '/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/edges.csv'
        edges_path = edges_path or '/Users/nicholas/Desktop/MSC_Works/DISSERTATION/Synthetic_Graph_Generator/Synthetic_Graph_Generator/Data/Dataverse/edges.csv'

        # nodes_path = nodes_path or '/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv'
        nodes_path = nodes_path or '/Users/nicholas/Desktop/MSC_Works/DISSERTATION/Synthetic_Graph_Generator/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv'

        g = pd.read_csv(edges_path)
        n = pd.read_csv(nodes_path)

        n = n.sort_values('node_index').reset_index(drop=True)
        node_order = n['node_index'].tolist()
        G = nx.from_pandas_edgelist(g, source='x_index', target='y_index')
        adj = nx.adjacency_matrix(G, nodelist=node_order)

        type_features = pd.get_dummies(n['node_type'], prefix='type', dtype=np.int8)
        features = type_features.to_numpy(dtype=np.float32)

        return adj, features

        


    else:
    # load the data: x, tx, allx, graph
        names = ['x', 'tx', 'allx', 'graph']
        objects = []
        for i in range(len(names)):
            with open("data/ind.{}.{}".format(dataset, names[i]), 'rb') as f:
                if sys.version_info > (3, 0):
                    objects.append(pkl.load(f, encoding='latin1'))
                else:
                    objects.append(pkl.load(f))
        x, tx, allx, graph = tuple(objects)
        test_idx_reorder = parse_index_file("data/ind.{}.test.index".format(dataset))
        test_idx_range = np.sort(test_idx_reorder)

        if dataset == 'citeseer':
            # Fix citeseer dataset (there are some isolated nodes in the graph)
            # Find isolated nodes, add them as zero-vecs into the right position
            test_idx_range_full = range(min(test_idx_reorder), max(test_idx_reorder)+1)
            tx_extended = sp.lil_matrix((len(test_idx_range_full), x.shape[1]))
            tx_extended[test_idx_range-min(test_idx_range), :] = tx
            tx = tx_extended

        features = sp.vstack((allx, tx)).tolil()
        features[test_idx_reorder, :] = features[test_idx_range, :]
        adj = nx.adjacency_matrix(nx.from_dict_of_lists(graph))


    return adj, features
