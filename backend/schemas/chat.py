from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    chat_history: List[ChatMessage] = []

class SourceItem(BaseModel):
    file_name: str
    page: Optional[int] = None
    excerpt: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem] = []
    grounded: bool
    abstained: bool
