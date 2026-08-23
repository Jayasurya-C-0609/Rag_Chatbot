import asyncio
from backend.core.logging import get_logger
from index import index_pdf, build_vector_database
from vectordb.delete_documents import delete_document
from config import MONGODB_DB_NAME, MONGODB_COLLECTION_NAME
import os
from pymongo import MongoClient

logger = get_logger(__name__)

class IndexingService:
    def __init__(self):
        self._lock = asyncio.Lock()

    async def index_document(self, file_path: str):
        async with self._lock:
            logger.info(f"Indexing document: {file_path}")
            index_pdf(file_path)

    async def rebuild_database(self):
        async with self._lock:
            logger.info("Rebuilding vector database...")
            build_vector_database("uploads")

    async def delete_document_from_db(self, filename: str, embedding_model):
        async with self._lock:
            logger.info(f"Deleting document from DB: {filename}")
            return delete_document(filename, embedding_model)
            
    async def clear_database(self):
        async with self._lock:
            logger.info("Clearing vector database...")
            uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_ATLAS_URI", "")
            db_name = os.getenv("DATABASE_NAME", MONGODB_DB_NAME)
            collection_name = os.getenv("COLLECTION_NAME", MONGODB_COLLECTION_NAME)
            if uri:
                client = MongoClient(uri)
                client[db_name][collection_name].delete_many({})

indexing_service = IndexingService()
