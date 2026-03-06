"""API endpoint tests.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check() -> None:
    """ verify health checkpoint returns status 200 and expected response. """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("api/v1/health")
        
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == "ok"
    assert data['agent'] == "main-agent"
    assert 'version' in data