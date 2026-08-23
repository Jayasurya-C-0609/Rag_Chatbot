from pydantic import BaseModel
from typing import List

class DocumentResponse(BaseModel):
    file_name: str
    
class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    
class StatusResponse(BaseModel):
    status: str
