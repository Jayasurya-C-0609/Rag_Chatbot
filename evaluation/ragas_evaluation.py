import json
import asyncio
import os

from dotenv import load_dotenv

from langchain_ollama import ChatOllama

from openai import AsyncOpenAI

from ragas.llms import llm_factory

from ragas.embeddings import HuggingFaceEmbeddings

from ragas.metrics.collections import (
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    AnswerRelevancy,
    AnswerCorrectness
)


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

ollama_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


ragas_llm = llm_factory(
    "qwen2.5:3b",
    provider="openai",
    client=ollama_client,
    max_tokens=2048
)
# =========================================================
# RAGAS EMBEDDINGS
# =========================================================

ragas_embeddings = HuggingFaceEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    device="cuda"
)


# =========================================================
# METRICS
# =========================================================

context_precision_metric = ContextPrecision(
    llm=ragas_llm
)

context_recall_metric = ContextRecall(
    llm=ragas_llm
)

faithfulness_metric = Faithfulness(
    llm=ragas_llm
)

answer_relevance_metric = AnswerRelevancy(
    llm=ragas_llm,
    embeddings=ragas_embeddings
)

answer_correctness_metric = AnswerCorrectness(
    llm=ragas_llm,
    embeddings=ragas_embeddings
)


# =========================================================
# LOAD SAVED RAG RESULTS
# =========================================================

def load_results():

    with open(
        "evaluation/evaluation_results.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# =========================================================
# ABSTENTION
# =========================================================

def is_abstention(answer):

    answer = answer.lower().strip()

    return (
        "i don't know based on the provided documents"
        in answer
        or
        "i do not know based on the provided documents"
        in answer
    )


def abstention_score(
    answer,
    answerable
):

    return int(
        is_abstention(answer)
        ==
        (not answerable)
    )


# =========================================================
# RUN ONE METRIC
# =========================================================

async def run_metric(
    metric,
    **kwargs
):

    try:

        result = await metric.ascore(
            **kwargs
        )

        return float(
            result.value
        )

    except Exception as e:

        print(
            "\nMetric Error:",
            type(e).__name__
        )

        print(e)

        return None


# =========================================================
# EVALUATE ONE SAMPLE
# =========================================================

async def evaluate_sample(sample):

    question = sample["question"]

    answer = sample["answer"]

    contexts = sample["contexts"]

    reference = sample.get(
        "reference_answer",
        ""
    )


    print("\n" + "=" * 60)

    print(
        "Question:",
        question
    )

    print("=" * 60)


    scores = {}


    # -----------------------------------------------------
    # Context Precision
    # -----------------------------------------------------

    scores["context_precision"] = await run_metric(

        context_precision_metric,

        user_input=question,

        retrieved_contexts=contexts,

        reference=reference
    )


    # -----------------------------------------------------
    # Context Recall
    # -----------------------------------------------------

    scores["context_recall"] = await run_metric(

        context_recall_metric,

        user_input=question,

        retrieved_contexts=contexts,

        reference=reference
    )


    # -----------------------------------------------------
    # Faithfulness
    # -----------------------------------------------------

    scores["faithfulness"] = await run_metric(

        faithfulness_metric,

        user_input=question,

        response=answer,

        retrieved_contexts=contexts
    )


    # -----------------------------------------------------
    # Answer Relevance
    # -----------------------------------------------------

    scores["answer_relevance"] = await run_metric(

        answer_relevance_metric,

        user_input=question,

        response=answer
    )


    # -----------------------------------------------------
    # Answer Correctness
    # -----------------------------------------------------

    scores["answer_correctness"] = await run_metric(

        answer_correctness_metric,

        user_input=question,

        response=answer,

        reference=reference
    )


    print(
        "Context Precision:",
        scores["context_precision"]
    )

    print(
        "Context Recall:",
        scores["context_recall"]
    )

    print(
        "Faithfulness:",
        scores["faithfulness"]
    )

    print(
        "Answer Relevance:",
        scores["answer_relevance"]
    )

    print(
        "Answer Correctness:",
        scores["answer_correctness"]
    )


    return scores


# =========================================================
# MAIN
# =========================================================

async def main():

    data = load_results()

    results = []

    abstention_scores = []


    print("\n" + "=" * 60)
    print("RAGAS EVALUATION FROM SAVED RESULTS")
    print("=" * 60)


    for sample in data:

        answerable = sample["answerable"]

        answer = sample["answer"]


        # -------------------------------------------------
        # Abstention
        # -------------------------------------------------

        abstention = abstention_score(
            answer,
            answerable
        )

        abstention_scores.append(
            abstention
        )


        print(
            "\nAbstention Correct:",
            abstention
        )


        # -------------------------------------------------
        # RAGAS
        # -------------------------------------------------

        if answerable:

            scores = await evaluate_sample(
                sample
            )

            results.append(
                scores
            )


    # =====================================================
    # AVERAGE
    # =====================================================

    def average(metric):

        values = [

            r[metric]

            for r in results

            if r[metric] is not None

        ]

        if not values:
            return 0.0

        return sum(values) / len(values)


    # =====================================================
    # FINAL RESULTS
    # =====================================================

    print("\n" + "=" * 60)
    print("FINAL RAGAS EVALUATION")
    print("=" * 60)


    print(
        "\nContext Precision:",
        round(
            average("context_precision"),
            4
        )
    )

    print(
        "Context Recall:",
        round(
            average("context_recall"),
            4
        )
    )

    print(
        "Faithfulness:",
        round(
            average("faithfulness"),
            4
        )
    )

    print(
        "Answer Relevance:",
        round(
            average("answer_relevance"),
            4
        )
    )

    print(
        "Answer Correctness:",
        round(
            average("answer_correctness"),
            4
        )
    )


    abstention_accuracy = (

        sum(abstention_scores)
        /
        len(abstention_scores)

        if abstention_scores
        else 0
    )


    print(
        "Abstention Accuracy:",
        round(
            abstention_accuracy,
            4
        )
    )


    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())