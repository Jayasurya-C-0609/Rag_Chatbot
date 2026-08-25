import os


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHROMA_DB_DIR = "chroma_db"

COLLECTION_NAME = "rag_documents"

LLM_MODEL = "openai/gpt-oss-120b"

UPLOAD_FOLDER = "uploads"


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    CHROMA_DB_DIR,
    exist_ok=True
)