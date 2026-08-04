import torch
import torch.nn.functional as F
from torch.optim import Adam
from sklearn.metrics import roc_auc_score, average_precision_score
import scipy.sparse as sp
import numpy as np
import os
import time

from input_data import load_data
from preprocessing import *
import args
import model

import argparse
import json
import sys
import time
import os

# Train on CPU (hide GPU) due to memory constraints
os.environ['CUDA_VISIBLE_DEVICES'] = ""

def parse_cli():
    p = argparse.ArgumentParser()
    p.add_argument("--edges_path", default=None)
    p.add_argument("--nodes_path", default=None)
    p.add_argument("--dataset", default=args.dataset)
    p.add_argument("--model", default=args.model)
    p.add_argument("--epochs", type=int, default=args.num_epoch)
    p.add_argument("--hidden1", type=int, default=args.hidden1_dim)
    p.add_argument("--hidden2", type=int, default=args.hidden2_dim)
    p.add_argument("--lr", type=float, default=args.learning_rate)
    p.add_argument("--checkpoint_out", default="vgae_checkpoint.pt")
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args()


cli = parse_cli()

if cli.seed is not None:
    torch.manual_seed(cli.seed)
    np.random.seed(cli.seed)

# override the shared args module so model.py picks up the right dims
args.dataset = cli.dataset
args.model = cli.model
args.num_epoch = cli.epochs
args.hidden1_dim = cli.hidden1
args.hidden2_dim = cli.hidden2
args.learning_rate = cli.lr

adj, features = load_data(args.dataset, edges_path=cli.edges_path, nodes_path=cli.nodes_path)

# Store original adjacency matrix (without diagonal entries) for later
adj_orig = adj
adj_orig = adj_orig - sp.dia_matrix((adj_orig.diagonal()[np.newaxis, :], [0]), shape=adj_orig.shape)
adj_orig.eliminate_zeros()

adj_train, train_edges, val_edges, val_edges_false, test_edges, test_edges_false = mask_test_edges(adj)
adj = adj_train

# Some preprocessing
adj_norm = preprocess_graph(adj)


num_nodes = adj.shape[0]

features = sparse_to_tuple(features.tocoo())
num_features = features[2][1]
features_nonzero = features[1].shape[0]

# This was never being set from the actual uploaded data, so the model was
# built with whatever stale default lives in args.py, and that wrong value
# then got written into the checkpoint and fed back into generate.py's
# load_model() -> repo_args.input_dim, which is where things go wrong later.
args.input_dim = num_features
# implement changes if above tcauses error
# features = sparse_to_tuple(features.tocoo() if sp.issparse(features) else sp.csr_matrix(features).tocoo())
# num_features = features[2][1]
# features_nonzero = features[1].shape[0]

# Create Model
pos_weight = float(adj.shape[0] * adj.shape[0] - adj.sum()) / adj.sum()
norm = adj.shape[0] * adj.shape[0] / float((adj.shape[0] * adj.shape[0] - adj.sum()) * 2)


adj_label = adj_train + sp.eye(adj_train.shape[0])
adj_label = sparse_to_tuple(adj_label)



adj_norm = torch.sparse.FloatTensor(torch.LongTensor(adj_norm[0].T), 
                            torch.FloatTensor(adj_norm[1]), 
                            torch.Size(adj_norm[2]))
adj_label = torch.sparse.FloatTensor(torch.LongTensor(adj_label[0].T), 
                            torch.FloatTensor(adj_label[1]), 
                            torch.Size(adj_label[2]))
features = torch.sparse.FloatTensor(torch.LongTensor(features[0].T), 
                            torch.FloatTensor(features[1]), 
                            torch.Size(features[2]))

# Densify once and reuse below. This used to be recomputed from the sparse
# tensor on every single epoch (once in the loss line, once inside get_acc),
# which is pure wasted CPU work that scales with graph size and is a big part
# of why training gets progressively slower on anything bigger than a toy graph.
adj_label_dense = adj_label.to_dense()

weight_mask = adj_label_dense.view(-1) == 1
weight_tensor = torch.ones(weight_mask.size(0)) 
weight_tensor[weight_mask] = pos_weight

# init model and optimizer
model = getattr(model,args.model)(adj_norm)
optimizer = Adam(model.parameters(), lr=args.learning_rate)


def get_scores(edges_pos, edges_neg, adj_rec):

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    # Predict on test set of edges
    preds = []
    pos = []
    for e in edges_pos:
        # print(e)
        # print(adj_rec[e[0], e[1]])
        preds.append(sigmoid(adj_rec[e[0], e[1]].item()))
        pos.append(adj_orig[e[0], e[1]])

    preds_neg = []
    neg = []
    for e in edges_neg:

        preds_neg.append(sigmoid(adj_rec[e[0], e[1]].data))
        neg.append(adj_orig[e[0], e[1]])

    preds_all = np.hstack([preds, preds_neg])
    labels_all = np.hstack([np.ones(len(preds)), np.zeros(len(preds_neg))])
    roc_score = roc_auc_score(labels_all, preds_all)
    ap_score = average_precision_score(labels_all, preds_all)

    return roc_score, ap_score

def get_acc(adj_rec, adj_label_dense):
    labels_all = adj_label_dense.view(-1).long()
    preds_all = (adj_rec > 0.5).view(-1).long()
    accuracy = (preds_all == labels_all).sum().float() / labels_all.size(0)
    return accuracy

# train model
for epoch in range(args.num_epoch):
    t = time.time()

    A_pred = model(features)
    optimizer.zero_grad()
    loss = log_lik = norm*F.binary_cross_entropy(A_pred.view(-1), adj_label_dense.view(-1), weight = weight_tensor)
    if args.model == 'VGAE':
        kl_divergence = 0.5/ A_pred.size(0) * (1 + 2*model.logstd - model.mean**2 - torch.exp(model.logstd)**2).sum(1).mean()
        loss -= kl_divergence

    loss.backward()
    optimizer.step()

    train_acc = get_acc(A_pred, adj_label_dense)

    val_roc, val_ap = get_scores(val_edges, val_edges_false, A_pred)
    print("Epoch:", '%04d' % (epoch + 1), "train_loss=", "{:.5f}".format(loss.item()),
          "train_acc=", "{:.5f}".format(train_acc), "val_roc=", "{:.5f}".format(val_roc),
          "val_ap=", "{:.5f}".format(val_ap),
          "time=", "{:.5f}".format(time.time() - t))


test_roc, test_ap = get_scores(test_edges, test_edges_false, A_pred)
print("End of training!", "test_roc=", "{:.5f}".format(test_roc),
      "test_ap=", "{:.5f}".format(test_ap))



# CHANGES ADDED BY Su-Styx


# Save and export 
# NOTE: this used to be hardcoded to "vgae_checkpoint.pt" regardless of the
# --checkpoint_out argument, which VGAE_endpoint.py always passes as an
# absolute, per-run UUID path. That meant every training run actually wrote
# its weights to the same relative filename in whatever the process's CWD
# happened to be -- so concurrent runs stomp on each other's checkpoint file,
# and VGAE_endpoint.py then looks for the checkpoint at the UUID path it was
# told about, which was never actually written, and raises FileNotFoundError
# (or worse, reads a different run's half-written file).
save_path = cli.checkpoint_out
torch.save({
    "model_state_dict": model.state_dict(),
    "optimizer_state_dict": optimizer.state_dict(),
    "dataset": args.dataset,
    "model_name": args.model,
    "epoch": args.num_epoch,
    "input_dim": args.input_dim,
    "hidden1_dim": args.hidden1_dim,
    "hidden2_dim": args.hidden2_dim,
    "num_nodes": num_nodes,
    "num_features": num_features,
}, save_path)

print(f"Weights saved to {save_path}")