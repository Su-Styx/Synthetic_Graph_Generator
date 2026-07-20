#api endpoint
import subprocess
import json
import os
import argparse
# from vgae_pytorch import generate
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from pathlib import Path



app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
GENERATE_SCRIPT = BASE_DIR / "vgae_pytorch" / "generate.py"

class VGAERequest(BaseModel):
    checkpoint: str #what checkpoint we want to use
    n: int = Field(...,ge=2) #node count, greater or equal to 2
    t: float = Field(...,gt=0.0,lt=1.0)#Threshold must be less than 1 and gt 0
    seed: Optional[int] = None


def generate(checkpoint: str, n: int, t: float, seed:Optional[int]= None) -> dict:
    cmd = [
        "python3",
        str(GENERATE_SCRIPT),
        "--checkpoint", checkpoint,
        "--num_nodes", str(n),
        "--threshold", str(t),
    ]


    if seed is not None:
        cmd += ["--seed", str(seed)]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return json.loads(result.stdout.strip())
    # G= subprocess.run(['python3','./generate.py',checkpoint,n,t])
    # print(G)


@app.post("/generate/VGAE")
async def vgae_endpoint(request:VGAERequest):
    try:
        return generate(
            checkpoint=request.checkpoint,
            n=request.n,
            t=request.t,
            seed=request.seed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

