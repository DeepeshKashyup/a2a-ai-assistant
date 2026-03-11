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

@pytest.mark.asyncio
async def test_version() -> None:
    """ verify version endpoint returns status 200 and expected response. """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("api/v1/version")
        
    assert response.status_code == 200
    data = response.json()
    assert 'version' in data

@pytest.mark.asyncio
async def test_chat() -> None:
    """ verify chat endpoint returns status 200 and expected response structure. """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"message": "What is the capital of France?", "session_id": "test-session"}
        response = await client.post("api/v1/chat", json=payload)
        
    assert response.status_code == 200
    data = response.json()
    assert 'reply' in data
    assert 'model' in data
    assert data['session_id'] == "test-session"