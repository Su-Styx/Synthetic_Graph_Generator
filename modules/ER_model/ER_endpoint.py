import networkx as nx
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ERRequest(BaseModel):
    n: int
    p: float
    directed: bool = False
    seed: Optional[int] = None

def generate_er_graph(n: int, p: float, directed: bool = False, seed: Optional[int] = None) -> dict:
    G = nx.erdos_renyi_graph(n=n, p=p, directed=directed, seed=seed)
    return {
        "nodes": [{"id": node} for node in G.nodes()],
        "edges": [{"source": u, "target": v} for u, v in G.edges()],
        "metadata": {
            "model": "erdos_renyi",
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "directed": directed,
            "parameters": {"n": n, "p": p, "seed": seed},
        },
    }
@app.post("/generate/erdos-renyi")
async def erdos_renyi_endpoint(request: ERRequest):
    return generate_er_graph(
        n=request.n,
        p=request.p,
        directed=request.directed,
        seed=request.seed,
    )

if __name__ == "__main__":
    import argparse
    import json
    import random

    parser = argparse.ArgumentParser(description="Train and generate using VGAE.")
    parser.add_argument("--n", type=int, required=True, help="number of nodes to generate")
    parser.add_argument("--p", type=float, required=True, help="p value (edge probability)")
    parser.add_argument("--directed", type=lambda x: x.lower() == "true", default=False, help="true | False")
    parser.add_argument("--seed", type=int, default=None, help="seed value")

    args = parser.parse_args()

    # Create RNG for NetworkX, but keep the original int seed for JSON
    rng = random.Random(args.seed) if args.seed is not None else None

    result = generate_er_graph(
        n=args.n,
        p=args.p,
        directed=args.directed,
        seed=rng,  # NetworkX gets the Random instance
    )

    # Put the original int seed back into the metadata for JSON serialization
    result["metadata"]["parameters"]["seed"] = args.seed

    print(json.dumps(result, indent=4))