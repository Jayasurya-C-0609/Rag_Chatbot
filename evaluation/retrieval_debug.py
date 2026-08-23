import json


FILE = "evaluation/evaluation_results.json"


TARGET_QUESTIONS = [
    "What is the purpose of the [SEP] token in BERT?",
    "Can a university nominate multiple AeroTHON 2026 teams?",
    "What qualifications must students have to participate in AeroTHON 2026?",
    "What are the eligibility requirements for AeroTHON 2026 team members and teams?"
]


def main():

    with open(
        FILE,
        "r",
        encoding="utf-8"
    ) as f:

        results = json.load(f)


    for result in results:

        question = result["question"]

        if question not in TARGET_QUESTIONS:
            continue


        print("\n" + "=" * 80)

        print(
            "QUESTION:",
            question
        )

        print("=" * 80)


        print("\nANSWER:")

        print(
            result["answer"]
        )


        print("\nREFERENCE:")

        print(
            result["reference_answer"]
        )


        print("\nRETRIEVED CONTEXTS:")

        for i, context in enumerate(
            result["contexts"],
            start=1
        ):

            print("\n" + "-" * 80)

            print(
                f"CONTEXT {i}"
            )

            print("-" * 80)

            print(context)


if __name__ == "__main__":

    main()