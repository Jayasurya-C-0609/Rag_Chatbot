import os

from langchain_core.prompts import ChatPromptTemplate
from retriever.reranker import rerank_documents

# -------------------------------------------------
# RAG prompt
# -------------------------------------------------
def build_rag_prompt():

    return ChatPromptTemplate.from_template(
        """
You are an AI assistant.

Use the conversation history to understand follow-up questions.

Answer ONLY from the provided context.

If the context contains enough information to answer the question, provide a concise explanation.

If the context partially answers the question, answer using only the available information and clearly state any limitation.

Only reply with "I don't know based on the provided documents." when the context contains no relevant information.

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
Rewrite the latest user question as a standalone question.

Use the conversation history to resolve references like
"it", "they", "that model", etc.

Do not answer the question.

Return only the rewritten question.
"""
            ),
            (
                "human",
                "Conversation history:\n{history}\n\nQuestion:\n{question}"
            )
        ]
    )


# -------------------------------------------------
# Rewrite follow-up question
# -------------------------------------------------
def rewrite_query(question, chat_history, llm):

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

        return rewritten.strip()

    return response.content.strip()


# -------------------------------------------------
# Main RAG pipeline
# -------------------------------------------------
def ask_question(question, chat_history, retriever, llm):

    # Rewrite follow-up question
    standalone_question = rewrite_query(
        question,
        chat_history,
        llm
    )

    print(f"Original: {question}")
    print(f"Standalone: {standalone_question}")

    # Use the normal MMR retriever
    candidate_docs = retriever.invoke(
        standalone_question
    )

    docs = rerank_documents(
        standalone_question,
        candidate_docs,
        top_k=4
    )

    print(f"Retrieved: {len(candidate_docs)}")
    print(f"After reranking: {len(docs)}")
    print(f"Retrieved chunks: {len(docs)}")

    # Build context
    context = format_context(docs)

    # Build conversation history
    history = ""

    for message in chat_history:

        history += (
            f"{message['role'].capitalize()}: "
            f"{message['content']}\n"
        )

    # Build prompt
    prompt = build_rag_prompt()

    messages = prompt.format_messages(
        context=context,
        question=standalone_question,
        history=history
    )

    # Generate answer
    response = llm.invoke(messages)

    if isinstance(response.content, list):

        answer = ""

        for item in response.content:

            if (
                isinstance(item, dict)
                and item.get("type") == "text"
            ):
                answer += item.get("text", "")

    else:

        answer = response.content

    # Collect sources
    sources = []

    for doc in docs:

        sources.append(
            {
                "file": os.path.basename(doc.metadata["source"]),
                "page": doc.metadata["page"] + 1
            }
        )

    return answer, sources