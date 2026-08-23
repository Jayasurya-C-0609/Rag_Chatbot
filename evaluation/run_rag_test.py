import json

from evaluation.test_questions import TEST_QUESTIONS

from embeddings.embedding_model import load_embedding_model
from retriever.hybrid_retriever import load_hybrid_retriever
from retriever.reranker import CrossEncoderReranker

from llm.llm import load_llm
from rag.rag_chain import ask_question


def generate_answer(
    question,
    retriever,
    llm,
    reranker
):

    answer = ""

    for result in ask_question(
        question,
        [],
        retriever,
        llm,
        reranker
    ):

        if result["type"] == "text":
            answer += result["content"]

    return answer.strip()


def get_contexts(
    question,
    retriever,
    reranker
):

    # -------------------------------------------------
    # Same retrieval pipeline
    # -------------------------------------------------

    docs = retriever.invoke(question)

    # -------------------------------------------------
    # Cross-encoder reranking
    # -------------------------------------------------

    reranked_results = reranker.rerank(
        question,
        docs,
        top_k=4
    )

    # -------------------------------------------------
    # Preserve top MMR candidates
    # -------------------------------------------------

    mmr_results = [
        (doc, 0.0)
        for doc in docs[:4]
    ]

    # -------------------------------------------------
    # Combine
    # -------------------------------------------------

    combined_results = (
        reranked_results +
        mmr_results
    )

    # -------------------------------------------------
    # Remove duplicate chunks
    # -------------------------------------------------

    seen = set()
    final_results = []

    for doc, score in combined_results:

        content = doc.page_content.strip()

        if content in seen:
            continue

        seen.add(content)

        final_results.append(
            (doc, score)
        )

        if len(final_results) >= 8:
            break

    # -------------------------------------------------
    # Return context text
    # -------------------------------------------------

    return [
        doc.page_content
        for doc, score in final_results
    ]


def main():

    print("\n" + "=" * 60)
    print("LOADING RAG SYSTEM")
    print("=" * 60)

    # -------------------------------------------------
    # Load components
    # -------------------------------------------------

    embedding_model = load_embedding_model()

    retriever = load_hybrid_retriever(
        embedding_model
    )

    reranker = CrossEncoderReranker()

    llm = load_llm()

    results = []

    print("\n" + "=" * 60)
    print("RUNNING RAG TEST")
    print("=" * 60)

    # -------------------------------------------------
    # Test every question
    # -------------------------------------------------

    for test in TEST_QUESTIONS:

        question = test["question"]

        print("\n" + "=" * 60)
        print("Question:", question)
        print("=" * 60)

        # -------------------------------------------------
        # Generate answer
        # -------------------------------------------------

        answer = generate_answer(
            question,
            retriever,
            llm,
            reranker
        )

        # -------------------------------------------------
        # Get the SAME retrieval context
        # -------------------------------------------------

        contexts = get_contexts(
            question,
            retriever,
            reranker
        )

        # -------------------------------------------------
        # Save result
        # -------------------------------------------------

        result = {
            "question": question,
            "answerable": test["answerable"],
            "reference_answer": test.get(
                "reference_answer",
                ""
            ),
            "answer": answer,
            "contexts": contexts
        }

        results.append(result)

        print("\nAnswer:")
        print(answer)

        print(
            "\nContexts:",
            len(contexts)
        )

    # -------------------------------------------------
    # Save results
    # -------------------------------------------------

    output_file = (
        "evaluation/evaluation_results.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print("RAG TEST COMPLETE")
    print("=" * 60)

    print(
        "\nSaved:",
        output_file
    )


if __name__ == "__main__":
    main()