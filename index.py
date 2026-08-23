import os

from loaders.pdf_loader import load_pdfs
from preprocess.splitter import split_documents
from embeddings.embedding_model import load_embedding_model
from vectordb.chroma_db import (
    create_vector_store,
    add_documents
)
from langchain_chroma import Chroma
from config import CHROMA_DB_DIR, COLLECTION_NAME


# ---------------------------------------------------
# Index a single PDF
# ---------------------------------------------------
def index_pdf(pdf_path):

    folder = os.path.dirname(pdf_path)
    filename = os.path.basename(pdf_path)

    print("=" * 50)
    print("Folder:", folder)
    print("Filename:", filename)

    documents = load_pdfs(folder)

    print(f"Total pages loaded: {len(documents)}")

    for doc in documents:
        print(doc.metadata)

    documents = [
        doc
        for doc in documents
        if os.path.basename(doc.metadata["source"]) == filename
    ]

    print(f"Filtered pages: {len(documents)}")

    chunks = split_documents(documents)

    print(f"Chunks created: {len(chunks)}")

    if not chunks:
        print("❌ No chunks created!")
        return

    print(chunks[0].metadata)

    embedding_model = load_embedding_model()

    try:
        add_documents(chunks, embedding_model)
        print("✅ Added documents to existing ChromaDB")

    except Exception as e:
        print(f"⚠️ Could not append to ChromaDB: {e}")
        print("Creating a new ChromaDB...")

        create_vector_store(chunks, embedding_model)

        print("✅ New ChromaDB created successfully")
# ---------------------------------------------------
# Build entire database
# ---------------------------------------------------
def build_vector_database(pdf_folder):

    documents = load_pdfs(pdf_folder)

    chunks = split_documents(documents)

    # Debug
    if chunks:
        print(chunks[0].metadata)

    embedding_model = load_embedding_model()

    # -------------------------------------------------
    # Delete existing Chroma collection
    # -------------------------------------------------

    if os.path.exists(CHROMA_DB_DIR):

        try:

            old_vector_store = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=embedding_model,
                collection_name=COLLECTION_NAME
            )

            old_vector_store.delete_collection()

            print("Old Chroma collection deleted.")

        except Exception as e:

            print(
                "Could not delete old collection:",
                e
            )

    # -------------------------------------------------
    # Create new vector store
    # -------------------------------------------------

    create_vector_store(
        chunks,
        embedding_model
    )

    print(
        f"Vector database rebuilt successfully."
    )