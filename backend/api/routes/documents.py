from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from backend.schemas.documents import DocumentListResponse, DocumentResponse, StatusResponse
from backend.services.document_service import document_service
from backend.services.indexing_service import indexing_service
from backend.api.dependencies import get_system_service
from backend.services.system_service import SystemService

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", response_model=DocumentListResponse)
def list_documents():
    docs = document_service.list_documents()
    return DocumentListResponse(documents=[DocumentResponse(file_name=doc) for doc in docs])

@router.get("/status", response_model=StatusResponse)
def document_status():
    docs = document_service.list_documents()
    return StatusResponse(status=f"Indexed {len(docs)} documents")

@router.post("/upload", response_model=StatusResponse)
async def upload_document(file: UploadFile = File(...), system: SystemService = Depends(get_system_service)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for upload API")
    
    # Sanitize filename to prevent path traversal
    import os
    safe_name = os.path.basename(file.filename)
    if "/" in file.filename or "\\" in file.filename or ".." in file.filename:
        file.filename = safe_name
        
    try:
        file_path = document_service.save_upload_file(file)
        await indexing_service.index_document(file_path)
        await system.refresh_retriever()
        return StatusResponse(status="indexed")
    except Exception as e:
        document_service.delete_local_file(safe_name)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{file_name}", response_model=StatusResponse)
async def delete_document(file_name: str, system: SystemService = Depends(get_system_service)):
    # Prevent path traversal
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        raise HTTPException(status_code=400, detail="Invalid file name")
        
    try:
        await indexing_service.delete_document_from_db(file_name, system.embedding_model)
        document_service.delete_local_file(file_name)
        await system.refresh_retriever()
        return StatusResponse(status="deleted")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rebuild", response_model=StatusResponse)
async def rebuild_documents(system: SystemService = Depends(get_system_service)):
    try:
        await indexing_service.rebuild_database()
        await system.refresh_retriever()
        return StatusResponse(status="rebuilt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("", response_model=StatusResponse)
async def clear_documents(system: SystemService = Depends(get_system_service)):
    try:
        await indexing_service.clear_database()
        document_service.clear_local_documents()
        await system.refresh_retriever()
        return StatusResponse(status="cleared")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
