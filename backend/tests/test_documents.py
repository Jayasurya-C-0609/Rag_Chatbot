import pytest

@pytest.mark.asyncio
async def test_list_documents(async_client):
    response = await async_client.get("/api/v1/documents")
    assert response.status_code == 200
    assert "documents" in response.json()

@pytest.mark.asyncio
async def test_document_status(async_client):
    response = await async_client.get("/api/v1/documents/status")
    assert response.status_code == 200
    assert "status" in response.json()
