import pytest

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    
@pytest.mark.asyncio
async def test_health_ready_not_initialized(async_client):
    response = await async_client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "initializing"}
