import os
import re

from langchain_core.prompts import ChatPromptTemplate
from retriever.reranker import remove_duplicate_documents
from utils.source_utils import extract_sources



def clean_model_output(text):

    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL
    )

    return text.strip()


# -------------------------------------------------
# RAG prompt
# -------------------------------------------------
def build_rag_prompt():

    return ChatPromptTemplate.from_template(
        """
You are a document-based AI assistant.

Answer the question using ONLY the provided context.

Rules:

- Do not use outside knowledge.
- Do not invent information.
- Do not add facts that are not supported by the context.
- Answer directly and clearly.
- If the context partially answers the question, use only
  the information available.
- If the context contains no relevant information, reply exactly:

"I don't know based on the provided documents."

Conversation History:
{history}

Context:
{context}

Question:
{question}

Answer:
"""
    )


# -------------------------------------------------
# Format retrieved documents
# -------------------------------------------------
def format_context(documents):

    return "\n\n".join(
        doc.page_content
        for doc in documents
    )


# -------------------------------------------------
# Query rewrite prompt
# -------------------------------------------------
def build_query_rewrite_prompt():

    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You rewrite user questions for document retrieval.

Your goal is to create a standalone retrieval query.

Rules:

1. If the user's question is already standalone and clear,
   return it unchanged.

2. Only rewrite the question when it contains a reference that
   requires conversation history, such as:
   "it", "this", "that", "they", "the previous model",
   "how does it work", or similar references.

3. Preserve the original meaning of the question.

4. Do not expand abbreviations unnecessarily.

5. Do not replace terms with their full names unless necessary
   to resolve ambiguity.

6. Do not add information that is not present in the question
   or conversation history.

7. Do not answer the question.

8. Return ONLY the standalone question.

Conversation History:
{history}
"""
            ),
            (
                "human",
                "Question:\n{question}"
            )
        ]
    )
# -------------------------------------------------
# Rewrite follow-up question
# -------------------------------------------------
def rewrite_query(question, chat_history, llm):
    
    if not chat_history:
        return question.strip()

    history = ""

    for message in chat_history:

        history += (
            f"{message['role'].capitalize()}: "
            f"{message['content']}\n"
        )

    prompt = build_query_rewrite_prompt()

    messages = prompt.format_messages(
        history=history,
        question=question
    )

    response = llm.invoke(messages)

    if isinstance(response.content, list):

        rewritten = ""

        for item in response.content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                rewritten += item.get("text", "")

            return clean_model_output(rewritten)

    return clean_model_output(response.content)


# -------------------------------------------------
# Main RAG pipeline
# -------------------------------------------------
def ask_question(question, chat_history, retriever, llm,reranker):

    # -------------------------------------------------
    # Rewrite follow-up question
    # -------------------------------------------------

    standalone_question = rewrite_query(
        question,
        chat_history,
        llm
    )

    print(f"Original: {question}")
    print(f"Standalone: {standalone_question}")

    # -------------------------------------------------
    # Retrieve documents
    # -------------------------------------------------

    # -------------------------------------------------
    # Retrieve candidate documents
    # -------------------------------------------------

    docs = retriever.invoke(
        standalone_question
    )

    print(
        f"Retrieved chunks: {len(docs)}"
    )

    # -------------------------------------------------
    # Cross-encoder reranking
    # -------------------------------------------------

    reranked_results = reranker.rerank(
        standalone_question,
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
    # Combine both
    # -------------------------------------------------

    combined_results = (
        reranked_results +
        mmr_results
    )

    # -------------------------------------------------
    # Remove duplicate chunks
    # -------------------------------------------------

    combined_results = remove_duplicate_documents(
        combined_results
    )

    # -------------------------------------------------
    # Final top K
    # -------------------------------------------------

    combined_results = combined_results[:8]

    
    reranked_docs = [
        doc
        for doc, score in combined_results
    ]


    print("\n" + "=" * 60)
    print("HYBRID RETRIEVAL RESULTS")
    print("=" * 60)

    for i, (doc, score) in enumerate(
        reranked_results,
        start=1
    ):

        print(
            i,
            os.path.basename(
                doc.metadata.get("source", "")
            ),
            "Page:",
            doc.metadata.get("page", 0) + 1,
            "Score:",
            float(score)
        )
    print(
        f"Reranked chunks: {len(reranked_docs)}"
    )


    # -------------------------------------------------
    # Build context
    # -------------------------------------------------

    context = format_context(reranked_docs)


    print("\n" + "=" * 60)
    print("FINAL CONTEXT SENT TO LLM")
    print("=" * 60)

    print(context)
    # -------------------------------------------------
    # Build prompt
    # -------------------------------------------------

    prompt = build_rag_prompt()

    history = ""

    for message in chat_history:

        history += (
            f"{message['role'].capitalize()}: "
            f"{message['content']}\n"
        )

    messages = prompt.format_messages(
        context=context,
        question=standalone_question,
        history=history
    )

    # -------------------------------------------------
    # Stream response
    # -------------------------------------------------

    for chunk in llm.stream(messages):

        if isinstance(chunk.content, str):

            yield {
                "type": "text",
                "content": chunk.content
            }

        elif isinstance(chunk.content, list):

            for item in chunk.content:

                if (
                    isinstance(item, dict)
                    and item.get("type") == "text"
                ):

                    yield {
                        "type": "text",
                        "content": item.get("text", "")
                    }

    # -------------------------------------------------
    # Sources
    # -------------------------------------------------

    sources = extract_sources(reranked_docs)

    yield {
        "type": "sources",
        "content": sources
    }