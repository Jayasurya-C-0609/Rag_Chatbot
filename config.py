EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# ---------------------------------------------------
# MongoDB Atlas Vector Store
# (values can be overridden by .env DATABASE_NAME / COLLECTION_NAME)
# ---------------------------------------------------
MONGODB_DB_NAME = "rag_db"
MONGODB_COLLECTION_NAME = "test"
MONGODB_INDEX_NAME = "vector_index"

LLM_MODEL = "openai/gpt-oss-20b"
