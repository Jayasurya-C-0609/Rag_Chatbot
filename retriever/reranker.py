from sentence_transformers import CrossEncoder

# Load once
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

def rerank_documents(question, documents, top_k=3):

    if not documents:

        return []

    pairs = []

    for doc in documents:

        pairs.append(
            (question, doc.page_content)
        )

    scores = reranker.predict(pairs)

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        doc
        for doc, _ in ranked[:top_k]
    ]