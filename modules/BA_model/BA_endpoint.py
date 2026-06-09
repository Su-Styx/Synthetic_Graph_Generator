
import networkx as nx
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

class BARequest(BaseModel):
    n: int
    m: int
    seed: Optional[int] = None

    @field_validator('m')
    @classmethod
    def m_must_be_less_than_n(cls, m, info):
        if 'n' in info.data and m >= info.data['n']:
            raise ValueError('m must be less than n')
        return m
    
    @field_validator('n')
    @classmethod
    def n_must_be_positive(cls, n):
        if n < 1:
            raise ValueError('n must be at least 1')
        return n

    @field_validator('m')
    @classmethod
    def m_must_be_positive(cls, m):
        if m < 1:
            raise ValueError('m must be at least 1')
        return m

def generate(n: int, m: int, seed: Optional[int] = None) -> dict:
    G = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
    return {
        "nodes": [{"id": node} for node in G.nodes()],
        "edges": [{"source": u, "target": v} for u, v in G.edges()],
        "metadata": {
            "model": "barabasi_albert",
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "directed": False,
            "parameters": {"n": n, "m": m}
        }
    }

@app.post("/generate/barabasi-albert")
async def barabasi_albert_endpoint(request: BARequest):
    return generate(n=request.n, m=request.m, seed=request.seed)