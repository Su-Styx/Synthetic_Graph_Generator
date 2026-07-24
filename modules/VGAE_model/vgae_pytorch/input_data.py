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

def load_data(dataset):
    # MY OWN CHANGES:
    if dataset =='disease_features':

        # RAN INTO MEMORY CONSTRAINTS
        # print('LOOK DISEASE DATASET FOUND')
        # g= pd.read_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/edges.csv')
        # n=pd.read_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv')


        # # building adj matrix 
        # G = nx.from_pandas_edgelist(g, source="x_index", target="y_index")
        # adj = nx.adjacency_matrix(G)

        # # building features matrix (F by N)
        # # dropped insignificant columns
        # n= n.drop('node_index', axis=1)
        # n=n.drop('node_source',axis=1)

        # type_encoded = pd.get_dummies(n['node_type'], prefix='type')
        # name_encoded = pd.get_dummies(n['node_name'], prefix='name')

        # features = pd.concat([type_encoded, name_encoded], axis=1)

        # # n['node_type'].str.encode('utf-8')
        # # n['node_name'].str.encode('utf-8')
        # # pd.factorize(n['node_type'])
        # features = features.to_numpy(dtype=np.float32)

        # STILL GET ERROR WITH THE FOLLOWING 
        # RUN train.py to test 8***************************************

        g = pd.read_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/edges.csv')
        n = pd.read_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv')

        n = n.sort_values('node_index').reset_index(drop=True)

        node_order = n['node_index'].tolist()
        G = nx.from_pandas_edgelist(g, source='x_index', target='y_index')

        adj = nx.adjacency_matrix(G, nodelist=node_order)

        type_features = pd.get_dummies(n['node_type'], prefix='type', dtype=np.int8)
        features = type_features.to_numpy(dtype=np.float32)






        # G = nx.from_pandas_edgelist(g, source="x_index", target="y_index")
        # adj = nx.adjacency_matrix(G)

        # n = n.sort_values('node_index').reset_index(drop=True)

        # # n= n.drop('node_index', axis=1)
        # n=n.drop('node_source',axis=1)

        # # n = n.sort_values('node_index').reset_index(drop=True)

        # type_features = pd.get_dummies(n['node_type'], prefix='type', dtype=np.int8)

        # features = type_features.to_numpy(dtype=np.float32)

        print(features.shape)
        print(type_features.head())

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
