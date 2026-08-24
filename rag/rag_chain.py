import os
import re

from langchain_core.prompts import ChatPromptTemplate
from retriever.reranker import remove_duplicate_documents
from utils.source_utils import extract_sources
from retriever.keyword_reranker import KeywordReranker
from collections import defaultdict

keyword_reranker = KeywordReranker()


def clean_model_output(text):

    # Remove Qwen thinking blocks
    text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Remove escaped <br> variants
    text = re.sub(
        r"\\+<br\s*/?>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove normal <br> variants
    text = re.sub(
        r"<br\s*/?>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # Remove excessive spaces
    text = re.sub(
        r"[ \t]{2,}",
        " ",
        text
    )

    return text.strip()
# -------------------------------------------------
# RAG prompt
# -------------------------------------------------
def build_rag_prompt():

    return ChatPromptTemplate.from_template(
        """
You are a document-based AI assistant.

Answer the user's question using ONLY the provided context.

Rules:

1. Use only information explicitly present in the context.
2. Do not use outside knowledge.
3. Do not invent or assume information.
4. If the answer is explicitly present in the context,
   give that answer directly.
5. For structured data such as CSV or tables, use the
   corresponding row or record to answer the question.
6. Ignore unrelated documents or passages in the context.
7. Answer at a level of detail appropriate to the question.
   For requests such as "explain clearly", provide the relevant
   details from the context rather than giving only a brief summary.
8. If the context does not contain enough information to answer,
   reply exactly:

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

    context = []

    for doc in documents:

        source = os.path.basename(
            doc.metadata.get("source", "Unknown")
        )

        page = doc.metadata.get("page")

        page = (
            page + 1
            if page is not None
            else "N/A"
        )

        context.append(
            f"[Source: {source} | Page: {page}]\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(context)
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

Create a standalone retrieval query when necessary.

Rules:

1. If the question is already clear and standalone,
   return it unchanged.

2. Use conversation history only when the current question
   depends on previous context.

3. If the question is independent, do not carry the previous
   topic into the question.

4. Preserve the original meaning.

5. Do not add unnecessary information.

6. Do not answer the question.

7. Return ONLY the rewritten question.

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



def reciprocal_rank_fusion(results, k=60):

    scores = defaultdict(float)
    documents = {}

    for result_list in results:

        for rank, (doc, _) in enumerate(
            result_list,
            start=1
        ):

            doc_id = doc.metadata.get(
                "chunk_id",
                (
                    doc.metadata.get("source", ""),
                    doc.metadata.get("page"),
                    doc.page_content[:100]
                )
            )

            scores[doc_id] += 1 / (k + rank)
            documents[doc_id] = doc

    ranked = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        (documents[doc_id], score)
        for doc_id, score in ranked
    ]


# -------------------------------------------------
# Main RAG pipeline
# -------------------------------------------------

def ask_question(
    question,
    chat_history,
    retriever,
    llm,
    reranker
):

    # Query rewrite
    standalone_question = rewrite_query(
        question,
        chat_history,
        llm
    )

    print(f"Original: {question}")
    print(f"Standalone: {standalone_question}")

    # -------------------------------------------------
    # Hybrid retrieval
    # -------------------------------------------------

    docs = retriever.invoke(
        standalone_question
    )

    print(
        f"Retrieved chunks: {len(docs)}"
    )

    # -------------------------------------------------
    # Cross Encoder
    # -------------------------------------------------

    cross_results = reranker.rerank(
        standalone_question,
        docs,
        top_k=15,
        score_threshold=-3.0
    )

    # -------------------------------------------------
    # Keyword Reranker
    # -------------------------------------------------

    keyword_results = keyword_reranker.rerank(
        standalone_question,
        docs,
        top_k=10
    )

    # -------------------------------------------------
    # MMR candidates
    # -------------------------------------------------

    mmr_results = [
        (doc, 0.0)
        for doc in docs[:8]
    ]

    # -------------------------------------------------
    # RRF Fusion
    # -------------------------------------------------

    fused_results = reciprocal_rank_fusion(
        [
            cross_results,
            keyword_results,
            mmr_results
        ]
    )

    # -------------------------------------------------
    # Final top 12
    # -------------------------------------------------

    selected = fused_results[:12]

    reranked_docs = [
        doc
        for doc, score in selected
    ]

    # -------------------------------------------------
    # Debug
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL RETRIEVAL SELECTION")
    print("=" * 60)

    for i, (doc, score) in enumerate(
        selected,
        start=1
    ):

        page = doc.metadata.get("page")

        page = (
            page + 1
            if page is not None
            else "N/A"
        )

        print(
            i,
            os.path.basename(
                doc.metadata.get(
                    "source",
                    "Unknown"
                )
            ),
            "| Page:",
            page,
            "| RRF:",
            round(float(score), 5)
        )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    context = format_context(
        reranked_docs
    )

    print("\n" + "=" * 60)
    print("FINAL CONTEXT")
    print("=" * 60)

    print(context)

    # -------------------------------------------------
    # Prompt
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
    # Generate answer
    # -------------------------------------------------

    response = llm.invoke(messages)

    if isinstance(response.content, str):
        full_response = response.content

    elif isinstance(response.content, list):

        full_response = ""

        for item in response.content:

            if isinstance(item, str):
                full_response += item

            elif isinstance(item, dict):
                full_response += item.get(
                    "text",
                    ""
                )

    else:
        full_response = str(
            response.content
        )

    full_response = clean_model_output(
        full_response
    )


    # -------------------------------------------------
    # Answer
    # -------------------------------------------------

    yield {
        "type": "text",
        "content": full_response
    }


    # -------------------------------------------------
    # Sources
    # -------------------------------------------------

    yield {
        "type": "sources",
        "content": extract_sources(
            reranked_docs
        )
    }