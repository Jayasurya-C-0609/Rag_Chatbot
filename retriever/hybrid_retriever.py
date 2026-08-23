from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from vectordb.mongodb_db import load_vector_store
from loaders.document_loader import load_documents
from preprocess.splitter import split_documents


def load_hybrid_retriever(embedding_model):

    # -------------------------------------------------
    # Semantic Retriever (MongoDB Atlas Vector Search)
    # -------------------------------------------------

    vector_store = load_vector_store(embedding_model)

    semantic_retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )

    # -------------------------------------------------
    # BM25 Retriever (in-memory keyword index)
    # -------------------------------------------------

    documents = load_documents("uploads")

    chunks = split_documents(documents)

    bm25_retriever = BM25Retriever.from_documents(chunks)

    bm25_retriever.k = 8

    # -------------------------------------------------
    # Hybrid Retriever
    # -------------------------------------------------

    hybrid = EnsembleRetriever(
        retrievers=[
            semantic_retriever,
            bm25_retriever
        ],
        weights=[
            0.6,
            0.4
        ]
    )

    return hybrid