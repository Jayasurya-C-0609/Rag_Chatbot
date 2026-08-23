import json


FILE = "evaluation/ragas_results.json"


def classify(result):

    problems = []

    if (
        result["context_precision"] is not None
        and result["context_precision"] < 0.70
    ):
        problems.append("LOW_CONTEXT_PRECISION")

    if (
        result["context_recall"] is not None
        and result["context_recall"] < 0.80
    ):
        problems.append("LOW_CONTEXT_RECALL")

    if (
        result["faithfulness"] is not None
        and result["faithfulness"] < 0.80
    ):
        problems.append("LOW_FAITHFULNESS")

    if (
        result["answer_relevance"] is not None
        and result["answer_relevance"] < 0.70
    ):
        problems.append("LOW_ANSWER_RELEVANCE")

    if (
        result["answer_correctness"] is not None
        and result["answer_correctness"] < 0.70
    ):
        problems.append("LOW_ANSWER_CORRECTNESS")

    return problems


def main():

    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:

        results = json.load(f)


    print("\n" + "=" * 70)
    print("RAG ERROR ANALYSIS")
    print("=" * 70)


    for i, result in enumerate(
        results,
        start=1
    ):

        problems = classify(result)

        if not problems:
            continue


        print("\n" + "-" * 70)

        print(
            f"{i}. {result['question']}"
        )

        print(
            "Context Precision:",
            result["context_precision"]
        )

        print(
            "Context Recall:",
            result["context_recall"]
        )

        print(
            "Faithfulness:",
            result["faithfulness"]
        )

        print(
            "Answer Relevance:",
            result["answer_relevance"]
        )

        print(
            "Answer Correctness:",
            result["answer_correctness"]
        )

        print(
            "Problems:",
            ", ".join(problems)
        )


    print("\n" + "=" * 70)
    print("ERROR ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()