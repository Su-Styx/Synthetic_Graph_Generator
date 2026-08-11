import pandas as pd 
import networkx as nx 

edges = pd.read_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Email-Eu/email-edges.txt',header=None, )

nodes = pd.read_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Email-Eu/email-node-dept.txt',sep=" ", header=None,)

# nodes=nodes.drop(columns=0)
# print('edges:')
# print(edges.head())

# print('nodes:')
# print(nodes.head(index=False))

edges.to_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Email-Eu/email-edges.csv', index=False)
nodes.to_csv('/home/styx/Dissertation/Synthetic_Graph_Generator/Data/Email-Eu/email-node-dept.csv', index=False)
