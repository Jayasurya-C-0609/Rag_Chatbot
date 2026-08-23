from vectordb.mongodb_db import load_vector_store


def load_retriever(embedding_model):

    vector_store = load_vector_store(embedding_model)

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    return retriever
