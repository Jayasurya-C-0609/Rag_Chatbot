import os

from loaders.file_loader import load_file, load_files
from preprocess.splitter import split_documents
from embeddings.embedding_model import load_embedding_model

from vectordb.chroma_db import (
    create_vector_store,
    add_documents
)

from langchain_chroma import Chroma
from config import CHROMA_DB_DIR, COLLECTION_NAME


# ---------------------------------------------------
# Index a single file
# ---------------------------------------------------

def index_file(file_path):

    filename = os.path.basename(file_path)

    print("=" * 50)
    print("File:", filename)

    # -----------------------------------------------
    # Load file using format-specific LangChain loader
    # -----------------------------------------------

    documents = load_file(file_path)

    print(
        f"Documents loaded: {len(documents)}"
    )

    if not documents:
        print("❌ No documents loaded!")
        return

    # -----------------------------------------------
    # Show metadata
    # -----------------------------------------------

    for doc in documents[:5]:
        print(doc.metadata)

    # -----------------------------------------------
    # Split documents
    # -----------------------------------------------

    chunks = split_documents(documents)

    print(
        f"Chunks created: {len(chunks)}"
    )

    if not chunks:
        print("❌ No chunks created!")
        return

    print(
        "First chunk metadata:",
        chunks[0].metadata
    )

    # -----------------------------------------------
    # Load embedding model
    # -----------------------------------------------

    embedding_model = load_embedding_model()

    # -----------------------------------------------
    # Add to existing ChromaDB
    # -----------------------------------------------

    try:

        add_documents(
            chunks,
            embedding_model
        )

        print(
            "✅ Documents added to existing ChromaDB"
        )

    except Exception as e:

        print(
            f"⚠️ Could not append to ChromaDB: {e}"
        )

        print(
            "Creating a new ChromaDB..."
        )

        create_vector_store(
            chunks,
            embedding_model
        )

        print(
            "✅ New ChromaDB created successfully"
        )


# ---------------------------------------------------
# Build entire database
# ---------------------------------------------------

def build_vector_database(folder):

    print("=" * 50)
    print("BUILDING VECTOR DATABASE")
    print("=" * 50)

    # -----------------------------------------------
    # Load all supported files
    # -----------------------------------------------

    documents = load_files(folder)

    print(
        f"Total documents loaded: {len(documents)}"
    )

    if not documents:
        print("❌ No documents found!")
        return

    # -----------------------------------------------
    # Split documents
    # -----------------------------------------------

    chunks = split_documents(
        documents
    )

    print(
        f"Total chunks created: {len(chunks)}"
    )

    if not chunks:
        print("❌ No chunks created!")
        return

    print(
        "First chunk metadata:",
        chunks[0].metadata
    )

    # -----------------------------------------------
    # Load embedding model
    # -----------------------------------------------

    embedding_model = load_embedding_model()

    # -----------------------------------------------
    # Delete existing Chroma collection
    # -----------------------------------------------

    if os.path.exists(CHROMA_DB_DIR):

        try:

            old_vector_store = Chroma(
                persist_directory=CHROMA_DB_DIR,
                embedding_function=embedding_model,
                collection_name=COLLECTION_NAME
            )

            old_vector_store.delete_collection()

            print(
                "Old Chroma collection deleted."
            )

        except Exception as e:

            print(
                "Could not delete old collection:",
                e
            )

    # -----------------------------------------------
    # Create new vector store
    # -----------------------------------------------

    create_vector_store(
        chunks,
        embedding_model
    )

    print(
        "✅ Vector database rebuilt successfully."
    )


# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    build_vector_database(
        "uploads"
    )