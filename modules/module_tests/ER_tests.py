# modules/tests/ER-tests.py

import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ER-model'))
from ER_endpoint import app

@pytest.mark.asyncio
async def test_er_returns_valid_graph():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post(
            "/generate/erdos-renyi",
            json={"n": 50, "p": 0.1, "seed": 42}
        )
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["metadata"]["model"] == "erdos_renyi"
    assert len(data["nodes"]) == 50