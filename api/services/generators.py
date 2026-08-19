# Model generation calls live here 
from modules.BA_model.BA_endpoint import generate as generate_BA_graph
from modules.ER_model.ER_endpoint import generate_er_graph 
from modules.ERGM_model.ERGM_endpoint import fit_and_generate_from_file as generate_ERGM_graph
from modules.VGAE_model.VGAE_endpoint import train_and_generate as generate_VGAE_graph

import json
import subprocess
from pathlib import Path
R_SCRIPT_PATH = Path("/home/styx/Dissertation/Synthetic_Graph_Generator/modules/ERGM_model/ERGM_fit_runner.R")


# wrap the return statement of each generation in attribute_gen


# def attribute_gen(labels:dict,graph:dict) ->dict:

#     n_l=labels["node_label"]
#     n_i=labels["node_ID"]
#     e_r=labels["edge_relationship"]
#     # optional section
#     n_a=labels["node_attribute"]
#     e_w=labels["edge_weight"]


#     n=graph["nodes"]
#     nodes=n[0]
#     edges=n[1]

#     for i in nodes:
        
#         # apply labelling for each of the nodes in the graph dict
#         pass
#     for j in edges:
#         # apply the edge labels 
#         pass





def generate_er(params: dict) -> dict:
    # nested generation function into attribute_gen to apply labels upon the returned dictionary
    # return attribute_gen(labels,generate_er_graph(
    #     n=params["n"],
    #     p=params["p"],
    #     directed=params.get("directed", False),
    #     seed=params.get("seed"),
    # ))

    return generate_er_graph(
        n=params["n"],
        p=params["p"],
        directed=params.get("directed", False),
        seed=params.get("seed"),
    )
# generate(n: int, p: float, directed: bool = False, seed: Optional[int] = None) -> dict:
#     G = nx.erdos_renyi_graph(n=n, p=p, directed=directed, seed=seed)


def generate_ba (params: dict) -> dict:
    return generate_BA_graph(
        n=params["n"],
        m=params["m"],
        seed=params.get("seed")
    )

def generate_ERGM_graph(file_path: str, seed: int | None = None) -> dict:
    seed_arg = str(seed) if seed is not None else "NA"

    result = subprocess.run(
        ["Rscript", str(R_SCRIPT_PATH), file_path, seed_arg],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=7200  # temp 2 hr testing,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ERGM fit/generate failed: {result.stderr.strip()}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"ERGM returned invalid JSON. stdout head: {result.stdout[:500]!r}, stderr head: {result.stderr[:500]!r}"
        ) from e

# directly call this one
def generate_ERGM(params: dict) -> dict:
    file_path = params["filepath"]
    seed = params.get("seed")
    return generate_ERGM_graph(file_path, seed)

# generators.py

# from .VGAE_endpoint import generate_VGAE_graph  # adjust import path as needed

def generate_VGAE(params: dict) -> dict:
    return generate_VGAE_graph(
        edges_path=params["filepath"],          # user’s edges CSV on disk
        nodes_path=params["nodes_filepath"],    # user’s nodes CSV on disk
        # n=params.get("n"),                      # or None for full size
        threshold=params["threshold"],
        model_name=params.get("model_name", "VGAE"),
        epochs=params.get("epochs", 200),
        hidden1=params.get("hidden1", 32),
        hidden2=params.get("hidden2", 16),
        lr=params.get("lr", 0.01),
        seed=params.get("seed"),
        checkpoint=params.get("checkpoint"),
    )