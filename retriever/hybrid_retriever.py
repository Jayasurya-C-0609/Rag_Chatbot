from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from vectordb.chroma_db import load_vector_store
from preprocess.splitter import split_documents
from loaders.file_loader import load_files


def load_hybrid_retriever(embedding_model):

    # -----------------------------------------------
    # Semantic Retriever
    # -----------------------------------------------

    vector_store = load_vector_store(
        embedding_model
    )

    semantic_retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 20,
            "fetch_k": 30,
            "lambda_mult": 0.70
        }
    )

    # -----------------------------------------------
    # BM25 Documents
    # -----------------------------------------------

    documents = load_files("uploads")

    chunks = split_documents(documents)
    
    if not chunks:
        return semantic_retriever

    print(
        f"BM25 chunks: {len(chunks)}"
    )

    # -----------------------------------------------
    # BM25
    # -----------------------------------------------

    bm25_retriever = BM25Retriever.from_documents(
        chunks
    )

    bm25_retriever.k = 20

    # -----------------------------------------------
    # Hybrid Retriever
    # -----------------------------------------------

    hybrid = EnsembleRetriever(
        retrievers=[
            semantic_retriever,
            bm25_retriever
        ],
        weights=[
            0.45,
            0.55
        ]
    )

    return hybrid