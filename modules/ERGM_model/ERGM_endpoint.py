import subprocess
import json
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

app = FastAPI()

R_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "ERGM_runner.R")

class ERGMRequest(BaseModel):
    n: int
    edges_coef: float = -3.0      # negative = sparse, positive = dense
    triangles_coef: float = 0.5   # positive = more clustering
    n_samples: int = 1
    seed: Optional[int] = None

    @field_validator('n')
    @classmethod
    def n_must_be_positive(cls, n):
        if n < 5:
            raise ValueError('n must be at least 5 for ERGM to be meaningful')
        return n

    @field_validator('n_samples')
    @classmethod
    def samples_must_be_positive(cls, n_samples):
        if n_samples < 1:
            raise ValueError('n_samples must be at least 1')
        return n_samples

def generate(
    n: int,
    edges_coef: float = -3.0,
    triangles_coef: float = 0.5,
    n_samples: int = 1,
    seed: Optional[int] = None
) -> dict:
    seed_arg = str(seed) if seed is not None else "NA"

    try:
        result = subprocess.run(
            [
                "Rscript", R_SCRIPT_PATH,
                str(n),
                str(edges_coef),
                str(triangles_coef),
                str(n_samples),
                seed_arg
            ],
            capture_output=True,
            text=True,
            timeout=120       # ERGM can be slow — 2 min ceiling
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="ERGM fitting timed out — try reducing n or adjusting coefficients"
        )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail=f"ERGM fitting failed: {result.stderr.strip()}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f"ERGM returned invalid JSON: {result.stdout[:200]}"
        )

@app.post("/generate/ergm")
async def ergm_endpoint(request: ERGMRequest):
    return generate(
        n=request.n,
        edges_coef=request.edges_coef,
        triangles_coef=request.triangles_coef,
        n_samples=request.n_samples,
        seed=request.seed
    )
