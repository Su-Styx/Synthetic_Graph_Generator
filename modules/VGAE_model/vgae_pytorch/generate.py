# A Su-Styx file 

import os 
import sys 
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)
import scipy.sparse as sp

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
# (additional changes)
def load_model(checkpoint_path, edges_path=None, nodes_path=None):
    print('model loaded')
    from input_data import load_data
    from preprocessing import preprocess_graph, sparse_to_tuple

    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    import args as repo_args
    repo_args.dataset     = checkpoint["dataset"]
    repo_args.input_dim   = checkpoint["input_dim"]
    repo_args.hidden1_dim = checkpoint["hidden1_dim"]
    repo_args.hidden2_dim = checkpoint["hidden2_dim"]

    # IMPORTANT: pass edges_path and nodes_path through
    adj, features = load_data(
        repo_args.dataset,
        edges_path=edges_path,
        nodes_path=nodes_path,
    )

    adj_norm = preprocess_graph(adj)
    adj_norm = torch.sparse.FloatTensor(
        torch.LongTensor(adj_norm[0].T),
        torch.FloatTensor(adj_norm[1]),
        torch.Size(adj_norm[2])
    )

    # features may be dense (numpy) or sparse; mirror train.py logic
    if sp.issparse(features):
        feats_coo = features.tocoo()
    else:
        feats_coo = sp.csr_matrix(features, dtype=np.float32).tocoo()

    feats_tuple = sparse_to_tuple(feats_coo)
    features = torch.sparse.FloatTensor(
        torch.LongTensor(feats_tuple[0].T),
        torch.FloatTensor(feats_tuple[1]),
        torch.Size(feats_tuple[2])
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
    For num_nodes_out == total number of nodes, we preserve
    the original node ordering so index i maps to the same node
    row as in the training data.
    """
    with torch.no_grad():
        # Encode using the real training data
        z = model.encode(features)   # z shape: (N, hidden2_dim)
        num_total = z.size(0)

        if num_nodes_out > num_total:
            raise ValueError(
                f"Requested {num_nodes_out} nodes but model has only {num_total}"
            )

        if num_nodes_out == num_total:
            # Use all nodes in original order (important for attribute pairing)
            z_sub = z
        else:
            # Subsample a subset of nodes (keeps generation behavior for smaller graphs)
            indices = torch.randperm(num_total)[:num_nodes_out]
            z_sub   = z[indices]

        # Decode via inner product
        adj_pred = torch.sigmoid(torch.mm(z_sub, z_sub.t()))
        adj_bin  = (adj_pred > threshold).int()
        adj_bin.fill_diagonal_(0)

    # Build edge list using local indices 0..num_nodes_out-1
    edges = adj_bin.nonzero(as_tuple=False).tolist()
    edges = [{"source": int(s), "target": int(t)} for s, t in edges if s < t]

    # Nodes here are index-only; we will attach attributes later in the endpoint
    nodes = [{"id": int(i)} for i in range(num_nodes_out)]

    return {
        "nodes":    nodes,
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
    parser.add_argument('--seed', type=int, default=5421)
    parser.add_argument('--edges_path', type=str, default=None)   # NEW
    parser.add_argument('--nodes_path', type=str, default=None)   # NEW
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


    model, features, ckpt = load_model(
    args.checkpoint,
    edges_path=args.edges_path,
    nodes_path=args.nodes_path,
    )
    graph = generate_graph(model, None, features, args.num_nodes, args.threshold)
    print(json.dumps(graph))