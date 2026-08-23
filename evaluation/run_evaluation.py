import os

from evaluation.test_questions import TEST_QUESTIONS

from evaluation.evaluator import (
    recall_at_k,
    precision_at_k,
    reciprocal_rank,
    evaluate_context_relevance,
    evaluate_faithfulness,
    evaluate_answer_relevance,
    evaluate_abstention
)

from embeddings.embedding_model import load_embedding_model

from retriever.hybrid_retriever import (
    load_hybrid_retriever
)

from retriever.reranker import (
    CrossEncoderReranker,
    remove_duplicate_documents
)

from llm.llm import load_llm

from rag.rag_chain import build_rag_prompt


# =====================================================
# LOAD LLM
# =====================================================

llm = load_llm()


# =====================================================
# GENERATE COMPLETE ANSWER
# =====================================================

def generate_answer(
    question,
    context,
    llm
):

    prompt = build_rag_prompt()

    messages = prompt.format_messages(
        context=context,
        question=question,
        history=""
    )

    response = llm.invoke(
        messages
    )

    # -------------------------------------------------
    # Extract text
    # -------------------------------------------------

    if isinstance(
        response.content,
        list
    ):

        answer = ""

        for item in response.content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):

                answer += item.get(
                    "text",
                    ""
                )

        return answer

    return response.content


# =====================================================
# LOAD MODELS
# =====================================================

embedding_model = load_embedding_model()

retriever = load_hybrid_retriever(
    embedding_model
)

reranker = CrossEncoderReranker()


# =====================================================
# ANSWERABLE METRICS
# =====================================================

answerable_before_rr = []

answerable_after_rr = []

answerable_before_precision = []

answerable_after_precision = []

answerable_context_relevance = []

answerable_faithfulness = []

answerable_answer_relevance = []


# =====================================================
# UNANSWERABLE METRICS
# =====================================================

unanswerable_abstention = []


# =====================================================
# EVALUATION
# =====================================================

for test in TEST_QUESTIONS:

    question = test["question"]

    # Graceful fallback if expected_files is missing from a test entry
    expected_files = test.get("expected_files", [])

    answerable = test["answerable"]


    # =================================================
    # INITIAL RETRIEVAL
    # =================================================

    docs = retriever.invoke(
        question
    )


    # =================================================
    # DEBUG RETRIEVED CANDIDATES
    # =================================================

    print()
    print("=" * 60)
    print("RETRIEVED CANDIDATES")
    print("=" * 60)

    print(
        "Total candidates:",
        len(docs)
    )

    for i, doc in enumerate(
        docs,
        start=1
    ):

        print(
            i,
            os.path.basename(
                doc.metadata.get(
                    "source",
                    ""
                )
            ),
            "Page:",
            doc.metadata.get(
                "page",
                0
            ) + 1
        )


    # =================================================
    # QUESTION INFORMATION
    # =================================================

    print()
    print("=" * 60)

    print(
        "Question:",
        question
    )

    print(
        "Expected:",
        expected_files
    )

    print(
        "Answerable:",
        answerable
    )

    print("=" * 60)


    # =================================================
    # BEFORE RERANKING
    # =================================================

    recall_before = recall_at_k(
        docs,
        expected_files,
        k=12
    )

    precision_before = precision_at_k(
        docs,
        expected_files,
        k=4
    )

    rr_before = reciprocal_rank(
        docs,
        expected_files
    )


    # =================================================
    # CROSS-ENCODER RERANKING
    # =================================================

    reranked_results = reranker.rerank(
        question,
        docs,
        top_k=8,
        score_threshold=-1.0
    )


    # =================================================
    # REMOVE DUPLICATES
    # =================================================

    reranked_results = remove_duplicate_documents(
        reranked_results
    )


    # =================================================
    # KEEP TOP 4
    # =================================================

    reranked_results = reranked_results[:4]


    # =================================================
    # EXTRACT DOCUMENTS
    # =================================================

    reranked_docs = [
        doc
        for doc, score in reranked_results
    ]


    # =================================================
    # AFTER RERANKING
    # =================================================

    precision_after = precision_at_k(
        reranked_docs,
        expected_files,
        k=4
    )

    rr_after = reciprocal_rank(
        reranked_docs,
        expected_files
    )


    # =================================================
    # BUILD FINAL CONTEXT
    # =================================================

    context = "\n\n".join(
        doc.page_content
        for doc in reranked_docs
    )


    # =================================================
    # GENERATE ANSWER
    # =================================================

    answer = generate_answer(
        question,
        context,
        llm
    )


    # =================================================
    # CONTEXT RELEVANCE
    # =================================================

    context_relevance = evaluate_context_relevance(
        question,
        context,
        llm
    )


    # =================================================
    # FAITHFULNESS
    # =================================================

    faithfulness = evaluate_faithfulness(
        question,
        context,
        answer,
        llm
    )


    # =================================================
    # ANSWER RELEVANCE
    # =================================================

    answer_relevance = evaluate_answer_relevance(
        question,
        answer,
        llm
    )


    # =================================================
    # ABSTENTION
    # =================================================

    abstention = evaluate_abstention(
        answer,
        answerable
    )


    # =================================================
    # STORE METRICS
    #
    # IMPORTANT:
    # Do NOT mix answerable and unanswerable
    # questions for retrieval/generation averages.
    # =================================================

    if answerable:

        # ---------------------------------------------
        # Answerable retrieval metrics
        # ---------------------------------------------

        answerable_before_rr.append(
            rr_before
        )

        answerable_after_rr.append(
            rr_after
        )

        answerable_before_precision.append(
            precision_before
        )

        answerable_after_precision.append(
            precision_after
        )


        # ---------------------------------------------
        # Answerable generation metrics
        # ---------------------------------------------

        answerable_context_relevance.append(
            context_relevance
        )

        answerable_faithfulness.append(
            faithfulness
        )

        answerable_answer_relevance.append(
            answer_relevance
        )

    else:

        # ---------------------------------------------
        # Only evaluate abstention for questions
        # that are expected to be unanswerable.
        # ---------------------------------------------

        unanswerable_abstention.append(
            abstention
        )


    # =================================================
    # PRINT BEFORE RERANKING
    # =================================================

    print()

    print(
        "BEFORE RERANKING"
    )

    print(
        "Recall@12:",
        recall_before
    )

    print(
        "Precision@4:",
        precision_before
    )

    print(
        "MRR:",
        rr_before
    )


    # =================================================
    # PRINT AFTER RERANKING
    # =================================================

    print()

    print(
        "AFTER RERANKING"
    )

    print(
        "Precision@4:",
        precision_after
    )

    print(
        "MRR:",
        rr_after
    )


    # =================================================
    # SHOW RERANKED DOCUMENTS
    # =================================================

    print()

    print(
        "Reranked documents:"
    )


    if reranked_results:

        for i, (doc, score) in enumerate(
            reranked_results,
            start=1
        ):

            print(
                i,
                os.path.basename(
                    doc.metadata.get(
                        "source",
                        ""
                    )
                ),
                "Page:",
                doc.metadata.get(
                    "page",
                    0
                ) + 1,
                "Score:",
                float(score)
            )

    else:

        print(
            "No documents selected."
        )


    # =================================================
    # GENERATED ANSWER
    # =================================================

    print()

    print(
        "GENERATED ANSWER"
    )

    print(
        answer
    )


    # =================================================
    # GENERATION EVALUATION
    # =================================================

    print()

    print(
        "Context Relevance:",
        context_relevance
    )

    print(
        "Faithfulness:",
        faithfulness
    )

    print(
        "Answer Relevance:",
        answer_relevance
    )

    print(
        "Abstention Correct:",
        abstention
    )


# =====================================================
# HELPER FUNCTION FOR AVERAGE
# =====================================================

def calculate_average(
    values
):

    if values:

        return (
            sum(values)
            / len(values)
        )

    return 0


# =====================================================
# ANSWERABLE RESULTS
# =====================================================

answerable_mrr_before = calculate_average(
    answerable_before_rr
)

answerable_mrr_after = calculate_average(
    answerable_after_rr
)

answerable_precision_before = calculate_average(
    answerable_before_precision
)

answerable_precision_after = calculate_average(
    answerable_after_precision
)

answerable_context_avg = calculate_average(
    answerable_context_relevance
)

answerable_faithfulness_avg = calculate_average(
    answerable_faithfulness
)

answerable_answer_relevance_avg = calculate_average(
    answerable_answer_relevance
)


# =====================================================
# UNANSWERABLE RESULTS
# =====================================================

abstention_accuracy = calculate_average(
    unanswerable_abstention
)


# =====================================================
# FINAL EVALUATION
# =====================================================

print()

print("=" * 60)

print(
    "FINAL EVALUATION"
)

print("=" * 60)


# =====================================================
# ANSWERABLE QUESTIONS
# =====================================================

print()

print(
    "ANSWERABLE QUESTIONS"
)

print("-" * 60)

print(
    "Number of answerable questions:",
    len(answerable_after_rr)
)

print()

print(
    "Precision@4 BEFORE:",
    answerable_precision_before
)

print(
    "Precision@4 AFTER:",
    answerable_precision_after
)

print(
    "MRR BEFORE:",
    answerable_mrr_before
)

print(
    "MRR AFTER:",
    answerable_mrr_after
)

print()

print(
    "Context Relevance:",
    answerable_context_avg
)

print(
    "Faithfulness:",
    answerable_faithfulness_avg
)

print(
    "Answer Relevance:",
    answerable_answer_relevance_avg
)


# =====================================================
# UNANSWERABLE QUESTIONS
# =====================================================

print()

print(
    "UNANSWERABLE QUESTIONS"
)

print("-" * 60)

print(
    "Number of unanswerable questions:",
    len(unanswerable_abstention)
)

print()

print(
    "Abstention Accuracy:",
    abstention_accuracy
)


# =====================================================
# END
# =====================================================

print()

print("=" * 60)

print(
    "EVALUATION COMPLETE"
)

print("=" * 60)