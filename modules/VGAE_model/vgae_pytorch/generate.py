# A Su-Styx file 

import os 
import sys 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

import torch 
import numpy as np
import random
import argparse
# from model import VGAE 
# from vgae_pytorch.model import VGAE
from model import VGAE
import json
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# import model 
def load_model(checkpoint_path):
    print('model loaded')
    from input_data import load_data
    from preprocessing import preprocess_graph, sparse_to_tuple

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    import args as repo_args
    repo_args.dataset = checkpoint["dataset"]
    repo_args.input_dim = checkpoint["input_dim"]
    repo_args.hidden1_dim = checkpoint["hidden1_dim"]
    repo_args.hidden2_dim = checkpoint["hidden2_dim"]

    adj, features = load_data(repo_args.dataset)
    adj_norm = preprocess_graph(adj)
    adj_norm = torch.sparse.FloatTensor(
        torch.LongTensor(adj_norm[0].T),
        torch.FloatTensor(adj_norm[1]),
        torch.Size(adj_norm[2])
    )

    features = sparse_to_tuple(features.tocoo())
    features = torch.sparse.FloatTensor(
        torch.LongTensor(features[0].T),
        torch.FloatTensor(features[1]),
        torch.Size(features[2])
    )

    from model import VGAE
    model = VGAE(adj_norm)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model, features, checkpoint

def generate_graph(model, adj_norm, features, num_nodes_out, threshold=0.5):
    print('graph generating')
    """
    Encode the training graph, sample from latent space,
    then decode to produce a new adjacency matrix.
    """
    with torch.no_grad():
        # Encode using the real training data
        z = model.encode(features)   # z shape: (2708, hidden2_dim)

        # Sample a subset of num_nodes_out latent vectors
        indices = torch.randperm(z.size(0))[:num_nodes_out]
        z_sub   = z[indices]

        # Decode via inner product
        adj_pred = torch.sigmoid(torch.mm(z_sub, z_sub.t()))
        adj_bin  = (adj_pred > threshold).int()
        adj_bin.fill_diagonal_(0)

    edges     = adj_bin.nonzero(as_tuple=False).tolist()
    edges     = [{"source": s, "target": t} for s, t in edges if s < t]

    return {
        "nodes":    [{"id": i} for i in range(num_nodes_out)],
        "edges":    edges,
        "metadata": {
            "model":    "vgae",
            "n_nodes":  num_nodes_out,
            "n_edges":  len(edges),
            "directed": False,
            "parameters": {"threshold": threshold}
        }
    }
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, default='./vgae_checkpoint.pt')
    parser.add_argument('--num_nodes',  type=int, default=20)
    parser.add_argument('--threshold',  type=float, default=0.5)
    parser.add_argument('--seed', type=int, default=5421) #default to reproducible output
    args = parser.parse_args()

    # random sampling handling w/ seed
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)
        torch.manual_seed(args.seed)
    
    #compliments endpoint invalid input handling
    if args.num_nodes < 2:
        raise ValueError("num_nodes must be at least 2")

    if not (0.0 < args.threshold < 1.0):
        raise ValueError("threshold must be between 0 and 1")


    model, features, ckpt = load_model(args.checkpoint)
    graph = generate_graph(model, None, features, args.num_nodes, args.threshold)
    print(json.dumps(graph))