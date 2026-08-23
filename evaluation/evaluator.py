import os

def parse_binary_score(text):

    text = text.strip()

    if text.startswith("1"):
        return 1

    if text.startswith("0"):
        return 0

    return 0


def recall_at_k(
    retrieved_docs,
    expected_files,
    k
):

    retrieved_docs = retrieved_docs[:k]

    retrieved_files = set()

    for doc in retrieved_docs:

        file = os.path.basename(
            doc.metadata.get("source", "")
        )

        retrieved_files.add(file)

    expected_files = set(expected_files)

    if retrieved_files.intersection(expected_files):

        return 1

    return 0



def precision_at_k(
    retrieved_docs,
    expected_files,
    k
):

    retrieved_docs = retrieved_docs[:k]

    if not retrieved_docs:
        return 0

    expected_files = set(expected_files)

    relevant_count = 0

    for doc in retrieved_docs:

        file = os.path.basename(
            doc.metadata.get(
                "source",
                ""
            )
        )

        if file in expected_files:

            relevant_count += 1

    return relevant_count / len(retrieved_docs)


def reciprocal_rank(
    retrieved_docs,
    expected_files
):

    expected_files = set(expected_files)

    for rank, doc in enumerate(
        retrieved_docs,
        start=1
    ):

        file = os.path.basename(
            doc.metadata.get("source", "")
        )

        if file in expected_files:

            return 1 / rank

    return 0


def evaluate_context_relevance(
        question,
        context,
        llm
    ):

        prompt = f"""
    You are evaluating a RAG retrieval system.

    Question:
    {question}

    Retrieved Context:
    {context}

    Is the retrieved context relevant for answering
    the question?

    Return ONLY:

    1

    or

    0

    1 = Relevant
    0 = Not relevant
    """

        response = llm.invoke(prompt)

        return parse_binary_score(
            response.content
    )


def evaluate_faithfulness(
        question,
        context,
        answer,
        llm
    ):

        prompt = f"""
    You are evaluating a RAG answer.

    Question:
    {question}

    Retrieved Context:
    {context}

    Generated Answer:
    {answer}

    Is the answer fully supported by the
    retrieved context?

    Return ONLY:

    1

    or

    0

    1 = Fully supported
    0 = Not fully supported
    """

        response = llm.invoke(prompt)

        return parse_binary_score(
            response.content
        )


# -------------------------------------------------
# Answer Relevance
# -------------------------------------------------

def evaluate_answer_relevance(
    question,
    answer,
    llm
):

    prompt = f"""
You are evaluating a RAG chatbot answer.

Question:
{question}

Generated Answer:
{answer}

Does the generated answer directly address
the user's question?

Return ONLY:

1

or

0

1 = The answer directly addresses the question
0 = The answer does not directly address the question
"""

    response = llm.invoke(prompt)

    return parse_binary_score(
        response.content
    )



# -------------------------------------------------
# Abstention Evaluation
# -------------------------------------------------

def evaluate_abstention(
    answer,
    answerable
):

    abstention_phrase = (
        "I don't know based on the provided documents."
    )

    did_abstain = (
        abstention_phrase.lower()
        in answer.lower()
    )

    # ---------------------------------------------
    # Answerable question
    # ---------------------------------------------

    if answerable:

        # We want the model to answer
        if did_abstain:
            return 0

        return 1

    # ---------------------------------------------
    # Unanswerable question
    # ---------------------------------------------

    else:

        # We want the model to abstain
        if did_abstain:
            return 1

        return 0