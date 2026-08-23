import os

from loaders.document_loader import load_documents
from preprocess.splitter import split_documents
from embeddings.embedding_model import load_embedding_model
from vectordb.mongodb_db import (
    create_vector_store,
    add_documents,
    load_vector_store,
)
from config import MONGODB_COLLECTION_NAME


# ---------------------------------------------------
# Index a single document (PDF / DOCX / TXT / CSV)
# ---------------------------------------------------
def index_pdf(pdf_path):
    """
    Index a single document file into MongoDB Atlas.
    The function name is kept as ``index_pdf`` for backward-compatibility
    but it now supports all document types handled by document_loader.
    """
    folder = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path)

    print("=" * 50)
    print("Folder:", folder)
    print("Filename:", filename)

    documents = load_documents(folder)

    print(f"Total pages loaded: {len(documents)}")

    # Filter to only the uploaded file
    documents = [
        doc
        for doc in documents
        if os.path.basename(doc.metadata.get("source", "")) == filename
    ]

    print(f"Filtered pages: {len(documents)}")

    if not documents:
        raise ValueError(
            f"No pages loaded from '{filename}'. "
            "The file may be empty or password-protected."
        )

    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    if not chunks:
        raise ValueError(
            f"No text extracted from '{filename}'. "
            "Check that the document contains readable text."
        )

    print(chunks[0].metadata)

    embedding_model = load_embedding_model()

    try:
        add_documents(chunks, embedding_model)
        print("✅ Added documents to MongoDB Atlas")

    except Exception as e:
        print(f"⚠️ Could not append to MongoDB: {e}")
        print("Creating a fresh vector store...")

        create_vector_store(chunks, embedding_model)

        print("✅ New MongoDB Atlas collection created successfully")


# ---------------------------------------------------
# Rebuild entire database from scratch
# ---------------------------------------------------
def build_vector_database(documents_folder):
    """
    Wipe the existing Atlas collection and re-index all documents
    found in ``documents_folder``.
    """
    documents = load_documents(documents_folder)

    if not documents:
        print(
            f"⚠️  No documents found in '{documents_folder}'. "
            "Nothing to index."
        )
        return

    chunks = split_documents(documents)

    if not chunks:
        print("⚠️  No text extracted from documents. Nothing to index.")
        return

    # Debug
    print(chunks[0].metadata)

    embedding_model = load_embedding_model()

    # create_vector_store drops the collection and re-inserts
    create_vector_store(chunks, embedding_model)

    print(
        f"Vector database rebuilt successfully in MongoDB Atlas "
        f"(collection: {MONGODB_COLLECTION_NAME})."
    )