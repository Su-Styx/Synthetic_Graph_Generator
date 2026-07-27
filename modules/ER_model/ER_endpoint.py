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