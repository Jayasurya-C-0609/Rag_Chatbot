from rag.rag_chain import ask_question
from backend.schemas.chat import ChatResponse, SourceItem, ChatMessage
import json
from typing import List

class ChatService:
    
    def process_chat(self, question: str, chat_history: List[ChatMessage], retriever, llm, reranker) -> ChatResponse:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in chat_history]
        
        answer = ""
        sources = []
        
        for result in ask_question(question, history_dicts, retriever, llm, reranker):
            if result["type"] == "text":
                answer += result["content"]
            elif result["type"] == "sources":
                sources = result["content"]
                
        abstained = "I don't know based on the provided documents" in answer
        grounded = not abstained
        
        source_items = [
            SourceItem(file_name=s["file"], page=s.get("page"), excerpt=s.get("excerpt"))
            for s in sources
        ]
        
        return ChatResponse(
            answer=answer,
            sources=source_items,
            grounded=grounded,
            abstained=abstained
        )
        
    async def stream_chat(self, question: str, chat_history: List[ChatMessage], retriever, llm, reranker):
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in chat_history]
        
        yield "event: status\ndata: \"Searching available documents...\"\n\n"
        
        try:
            first_token = True
            for result in ask_question(question, history_dicts, retriever, llm, reranker):
                if result["type"] == "text":
                    if first_token:
                        yield "event: status\ndata: \"Generating grounded answer...\"\n\n"
                        first_token = False
                    yield f"event: token\ndata: {json.dumps(result['content'])}\n\n"
                elif result["type"] == "sources":
                    source_items = [
                        {"file_name": s["file"], "page": s.get("page"), "excerpt": s.get("excerpt")}
                        for s in result["content"]
                    ]
                    yield f"event: source\ndata: {json.dumps(source_items)}\n\n"
            
            yield "event: done\ndata: \"\"\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps(str(e))}\n\n"

chat_service = ChatService()
