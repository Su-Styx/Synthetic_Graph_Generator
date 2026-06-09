import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'BA_model'))
from BA_endpoint import app

@pytest.mark.asyncio
async def test_ba_returns_valid_graph():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/barabasi-albert",
            json={"n": 50, "m": 2, "seed": 42}
        )
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["metadata"]["model"] == "barabasi_albert"
    assert len(data["nodes"]) == 50

@pytest.mark.asyncio
async def test_ba_edge_count_matches_expectation():
    """BA with m=2 should produce exactly (n-m)*m edges"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/barabasi-albert",
            json={"n": 50, "m": 2, "seed": 42}
        )
    data = response.json()
    expected_edges = (50 - 2) * 2
    assert len(data["edges"]) == expected_edges

@pytest.mark.asyncio
async def test_ba_rejects_m_greater_than_n():
    """m >= n should return a 422 validation error"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/barabasi-albert",
            json={"n": 5, "m": 10}
        )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_ba_seed_reproducibility():
    """Same seed should produce identical graphs"""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        r1 = await client.post(
            "/generate/barabasi-albert",
            json={"n": 50, "m": 2, "seed": 99}
        )
        r2 = await client.post(
            "/generate/barabasi-albert",
            json={"n": 50, "m": 2, "seed": 99}
        )
    assert r1.json()["edges"] == r2.json()["edges"]