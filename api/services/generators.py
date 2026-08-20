# Model generation calls live here 
from modules.BA_model.BA_endpoint import generate as generate_BA_graph
from modules.ER_model.ER_endpoint import generate_er_graph 
from modules.ERGM_model.ERGM_endpoint import fit_and_generate_from_file as generate_ERGM_graph
from modules.VGAE_model.VGAE_endpoint import train_and_generate as generate_VGAE_graph
from typing import Optional 
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



from pathlib import Path
from django.conf import settings

def generate_ERGM_graph(file_path: str, seed: Optional[int] = None) -> dict:
    abs_path = Path(settings.MEDIA_ROOT) / file_path
    if not abs_path.exists():
        raise FileNotFoundError(f"ERGM input file not found: {abs_path}")

    script_path = "/app/modules/ERGM_model/ERGM_fit_runner.R"
    seed_arg = str(seed) if seed is not None else "NA"
    output_path = abs_path.with_suffix(abs_path.suffix + ".result.json")

    cmd = ["Rscript", script_path, str(abs_path), seed_arg, "AUTO", str(output_path)]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=7200)

    # Always log what happened, regardless of outcome
    print(f"ERGM subprocess returncode={result.returncode}")
    print(f"ERGM stdout: {result.stdout[:1000]}")
    print(f"ERGM stderr: {result.stderr[-2000:]}")  # tail is more useful for R logs

    if not output_path.exists():
        raise RuntimeError(
            f"ERGM did not produce an output file (returncode={result.returncode}). "
            f"stdout: {result.stdout[:500]!r}, stderr tail: {result.stderr[-1500:]!r}"
        )

    try:
        with output_path.open() as f:
            return json.load(f)
    finally:
        output_path.unlink(missing_ok=True)  # cleanup
# def generate_ERGM_graph(file_path: str, seed: int | None = None) -> dict:
#     seed_arg = str(seed) if seed is not None else "NA"
    

#     result = subprocess.run(
#         ["Rscript", str(R_SCRIPT_PATH), file_path, seed_arg],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True,
#         timeout=7200  # temp 2 hr testing,
#     )

#     if result.returncode != 0:
#         raise RuntimeError(f"ERGM fit/generate failed: {result.stderr.strip()}")

#     try:
#         return json.loads(result.stdout)
#     except json.JSONDecodeError as e:
#         raise RuntimeError(
#             f"ERGM returned invalid JSON. stdout head: {result.stdout[:500]!r}, stderr head: {result.stderr[:500]!r}"
#         ) from e

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
        n=params.get("n"),                      # or None for full size
        threshold=params["threshold"],
        model_name=params.get("model_name", "VGAE"),
        epochs=params.get("epochs", 200),
        hidden1=params.get("hidden1", 32),
        hidden2=params.get("hidden2", 16),
        lr=params.get("lr", 0.01),
        seed=params.get("seed"),
        checkpoint=params.get("checkpoint"),
    )