import pandas as pd
import networkx as nx

edges = pd.read_csv("/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/edges.csv")
nodes = pd.read_csv("/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/nodes.csv")

selected_nodes = set(nodes["node_index"].head(3000))
# 3500 nodes and 200 epochs provide:
# test_roc= 0.78136 test_ap= 0.78987

# 4,000 nodes and 200 epochs provide:
# test_roc= 0.78463 test_ap= 0.79378 

# 5,000 nodes and 200 epochs provide: 
# test_roc= 0.78555 test_ap= 0.79544
# requires about 50gb of memory to run
# 5k with 2000 epochs and lr= 0.0025: test_roc= 0.78383 test_ap= 0.79252, saw highs of .8




filtered_edges = edges[
    edges["x_index"].isin(selected_nodes)
    & edges["y_index"].isin(selected_nodes)
].copy()

used_nodes = set(filtered_edges["x_index"]).union(
    filtered_edges["y_index"]
)

filtered_nodes = nodes[
    nodes["node_index"].isin(used_nodes)
].copy()

filtered_edges.to_csv("/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/edges_3000.csv", index=False)
filtered_nodes.to_csv("/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Dataverse/nodes_3000.csv", index=False)
