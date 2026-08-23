import os

from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch

from config import (
    MONGODB_DB_NAME,
    MONGODB_COLLECTION_NAME,
    MONGODB_INDEX_NAME,
)

load_dotenv()


# ---------------------------------------------------
# Internal helpers
# ---------------------------------------------------

def _get_collection():
    """Return the pymongo Collection object."""
    # Support both MONGODB_URI (user's .env) and MONGODB_ATLAS_URI
    uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_ATLAS_URI")
    if not uri:
        raise EnvironmentError(
            "MONGODB_URI is not set. "
            "Add it to your .env file."
        )
    # Allow .env overrides for db/collection names
    db_name = os.getenv("DATABASE_NAME", MONGODB_DB_NAME)
    collection_name = os.getenv("COLLECTION_NAME", MONGODB_COLLECTION_NAME)
    client = MongoClient(uri)
    return client[db_name][collection_name]


def _get_vector_store(embedding_model, collection):
    """Wrap a pymongo collection as a LangChain vector store."""
    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=embedding_model,
        index_name=MONGODB_INDEX_NAME,
        text_key="page_content",
        embedding_key="embedding",
    )


# ---------------------------------------------------
# Public API  (mirrors the old chroma_db.py interface)
# ---------------------------------------------------

def load_vector_store(embedding_model):
    """Load the existing Atlas collection as a vector store."""
    collection = _get_collection()
    return _get_vector_store(embedding_model, collection)


def create_vector_store(chunks, embedding_model):
    """
    Drop the existing collection content and create a fresh vector store
    from the supplied chunks.
    """
    collection = _get_collection()

    # Clear existing documents before rebuilding
    collection.delete_many({})

    ids = [chunk.metadata["chunk_id"] for chunk in chunks]

    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection=collection,
        index_name=MONGODB_INDEX_NAME,
        text_key="page_content",
        embedding_key="embedding",
    )

    return vector_store


def add_documents(chunks, embedding_model):
    """
    Upsert new chunks into the existing Atlas collection.
    Skips chunks whose chunk_id already exists to avoid duplicates.
    """
    collection = _get_collection()

    # Find already-indexed chunk IDs
    existing_ids = {
        doc["chunk_id"]
        for doc in collection.find(
            {"chunk_id": {"$exists": True}},
            {"chunk_id": 1, "_id": 0}
        )
    }

    new_chunks = [
        chunk
        for chunk in chunks
        if chunk.metadata.get("chunk_id") not in existing_ids
    ]

    if not new_chunks:
        print("All chunks already indexed — nothing to add.")
        vector_store = _get_vector_store(embedding_model, collection)
        return vector_store

    vector_store = MongoDBAtlasVectorSearch.from_documents(
        documents=new_chunks,
        embedding=embedding_model,
        collection=collection,
        index_name=MONGODB_INDEX_NAME,
        text_key="page_content",
        embedding_key="embedding",
    )

    print(f"Added {len(new_chunks)} new chunks to MongoDB Atlas.")
    return vector_store
