import pytest

@pytest.mark.asyncio
async def test_chat_uninitialized(async_client):
    # Should return 503 if system service models (retriever) are not loaded
    response = await async_client.post(
        "/api/v1/chat", 
        json={"question": "What is AI?", "chat_history": []}
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "HTTP_ERROR"
