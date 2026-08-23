import os
import shutil
from fastapi import UploadFile
from backend.core.config import settings
from backend.core.logging import get_logger
from utils.file_manager import get_uploaded_pdfs
from utils.startup import ensure_uploads_dir

logger = get_logger(__name__)

class DocumentService:
    def __init__(self):
        ensure_uploads_dir()

    def save_upload_file(self, upload_file: UploadFile) -> str:
        file_path = os.path.join("uploads", upload_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return file_path

    def delete_local_file(self, filename: str):
        file_path = os.path.join("uploads", filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    def list_documents(self):
        return get_uploaded_pdfs()
        
    def clear_local_documents(self):
        if os.path.exists("uploads"):
            for filename in os.listdir("uploads"):
                file_path = os.path.join("uploads", filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)

document_service = DocumentService()
