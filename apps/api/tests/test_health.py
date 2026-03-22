import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "TaskFlow API"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check_returns_version(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["version"] == "0.1.0"
