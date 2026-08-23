from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.chat_service import chat_service
from backend.api.dependencies import get_system_service
from backend.services.system_service import SystemService

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, system: SystemService = Depends(get_system_service)):
    if not system.retriever:
        raise HTTPException(status_code=503, detail="System not fully initialized")
        
    return chat_service.process_chat(
        question=request.question,
        chat_history=request.chat_history,
        retriever=system.retriever,
        llm=system.llm,
        reranker=system.reranker
    )

@router.post("/stream")
async def chat_stream(request: ChatRequest, system: SystemService = Depends(get_system_service)):
    if not system.retriever:
        raise HTTPException(status_code=503, detail="System not fully initialized")
        
    return StreamingResponse(
        chat_service.stream_chat(
            question=request.question,
            chat_history=request.chat_history,
            retriever=system.retriever,
            llm=system.llm,
            reranker=system.reranker
        ),
        media_type="text/event-stream"
    )
