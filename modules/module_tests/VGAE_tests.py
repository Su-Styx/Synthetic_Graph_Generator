import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'VGAE_model'))
from VGAE_endpoint import app

CHECKPOINT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'VGAE_model', 'vgae_pytorch', 'vgae_checkpoint.pt'
))



@pytest.mark.asyncio 
async def test_VGAE_returns_valid_graph():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client: 
        response = await client.post("/generate/VGAE",json={'checkpoint': CHECKPOINT,'n':20,'t':0.5}) 
    assert response.status_code ==200
    data = response.json()
    assert "nodes"    in data  
    assert "edges"    in data   
    assert "metadata" in data   

    meta = data["metadata"]
    assert meta["model"]    == "vgae"   
    assert meta["n_nodes"]  == 20      
    assert meta["n_edges"]  == len(data["edges"])  
    assert meta["directed"] is False

    # print(data)
    # assert data[]


# data output format:

# {"nodes": [ {id:0...etc}],"edges":[{"source":0,"target":1}...etc],
# "metadata":{"model": "vgae", "n_nodes": 20, "n_edges": 98, "directed": false,"parameters": {"threshold": 0.5}}}

@pytest.mark.asyncio
async def test_vgae_seed_reproducibility():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r1 = await client.post(
            "/generate/VGAE",
            json={"checkpoint": CHECKPOINT, "n": 20, "t": 0.5, "seed": 99}
        )
        r2 = await client.post(
            "/generate/VGAE",
            json={"checkpoint": CHECKPOINT, "n": 20, "t": 0.5, "seed": 99}
        )

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["edges"] == r2.json()["edges"]

@pytest.mark.asyncio
async def test_vgae_threshold_affects_density():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r1 = await client.post(
            "/generate/VGAE",
            json={"checkpoint": CHECKPOINT, "n": 20, "t": 0.3, "seed": 54}
        )
        r2 = await client.post(
            "/generate/VGAE",
            json={"checkpoint": CHECKPOINT, "n": 20, "t": 0.8, "seed": 54}
        )

    assert r1.status_code == 200
    assert r2.status_code == 200

    data1 = r1.json()
    data2 = r2.json()

    assert len(data2["edges"]) <= len(data1["edges"])


@pytest.mark.asyncio
async def test_vgae_rejects_invalid_threshold():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/VGAE",
            json={"checkpoint": CHECKPOINT, "n": 20, "t": 1.5}
        )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_vgae_rejects_small_n():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/VGAE",
            json={"checkpoint": CHECKPOINT, "n": 1, "t": 0.5}
        )

    assert response.status_code == 422
    