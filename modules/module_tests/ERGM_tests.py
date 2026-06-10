import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ERGM_model'))
from ERGM_endpoint import app

@pytest.mark.asyncio
async def test_ergm_returns_valid_graph():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/ergm",
            json={"n": 20, "edges_coef": -3.0, "triangles_coef": 0.5, "seed": 42}
        )
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["metadata"]["model"] == "ergm"
    assert len(data["nodes"]) == 20

@pytest.mark.asyncio
async def test_ergm_rejects_small_n():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/ergm",
            json={"n": 3, "edges_coef": -3.0}
        )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_ergm_seed_reproducibility():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r1 = await client.post(
            "/generate/ergm",
            json={"n": 20, "edges_coef": -3.0, "triangles_coef": 0.0, "seed": 7}
        )
        r2 = await client.post(
            "/generate/ergm",
            json={"n": 20, "edges_coef": -3.0, "triangles_coef": 0.0, "seed": 7}
        )
    assert r1.json()["edges"] == r2.json()["edges"]
