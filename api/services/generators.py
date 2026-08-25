# Model generation calls live here, some renamed 
from modules.BA_model.BA_endpoint import generate as generate_BA_graph
from modules.ER_model.ER_endpoint import generate_er_graph 
from modules.ERGM_model.ERGM_endpoint import fit_and_generate_from_file as generate_ERGM_graph
from modules.VGAE_model.VGAE_endpoint import train_and_generate as generate_VGAE_graph
from typing import Optional 
import json
import subprocess
from pathlib import Path
from django.conf import settings


# NOTE: for dockerdeployment, remove line below and make relative to root dir
# R_SCRIPT_PATH = Path("/home/styx/Dissertation/Synthetic_Graph_Generator/modules/ERGM_model/ERGM_fit_runner.R")


# wrap the return statement of each generation in attribute_gen


def generate_er(params: dict) -> dict:

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





def generate_ERGM_graph(file_path: str, seed: Optional[int] = None) -> dict:
    abs_path = Path(settings.MEDIA_ROOT) / file_path
    if not abs_path.exists():
        raise FileNotFoundError(f"ERGM input file not found: {abs_path}")

    script_path = "/app/modules/ERGM_model/ERGM_fit_runner.R"
    seed_arg = str(seed) if seed is not None else "NA"
    output_path = abs_path.with_suffix(abs_path.suffix + ".result.json")

    cmd = ["Rscript", script_path, str(abs_path), seed_arg, "AUTO", str(output_path)]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=7200)

    # logging everything that happens, volatile in docker container 
    # show early and last few parts to get where it wernt wrong
    print(f"ERGM subprocess returncode={result.returncode}")
    print(f"ERGM stdout: {result.stdout[:1000]}")
    print(f"ERGM stderr: {result.stderr[-2000:]}")  

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

# directly call this one
def generate_ERGM(params: dict) -> dict:
    file_path = params["filepath"]
    seed = params.get("seed")
    return generate_ERGM_graph(file_path, seed)




def generate_VGAE(params: dict) -> dict:
    # added some defaults for prompting directly from cli 

    edges_path = Path(settings.MEDIA_ROOT) / params["filepath"]
    nodes_path = Path(settings.MEDIA_ROOT) / params["nodes_filepath"]

    if not edges_path.exists():
        raise FileNotFoundError(f"VGAE edges file not found: {edges_path}")
    if not nodes_path.exists():
        raise FileNotFoundError(f"VGAE nodes file not found: {nodes_path}")
    return generate_VGAE_graph(
        edges_path=str(edges_path),
        nodes_path=str(nodes_path),
        # edges_path=params["filepath"],          
        # nodes_path=params["nodes_filepath"],    
        n=params.get("n"),                     
        threshold=params["threshold"],
        model_name=params.get("model_name", "VGAE"),
        epochs=params.get("epochs", 200),
        hidden1=params.get("hidden1", 32),
        hidden2=params.get("hidden2", 16),
        lr=params.get("lr", 0.01),
        seed=params.get("seed"),
        checkpoint=params.get("checkpoint"),
    )