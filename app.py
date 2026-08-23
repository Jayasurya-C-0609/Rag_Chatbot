import asyncio
import nest_asyncio

# Patch the event loop to prevent 'Event loop is closed' RuntimeError
# that occurs when Streamlit's script runner interacts with asyncio libs.
nest_asyncio.apply()

import os
import shutil
import streamlit as st

from utils.startup import ensure_uploads_dir, validate_env
from embeddings.embedding_model import load_embedding_model
from retriever.hybrid_retriever import load_hybrid_retriever
from llm.llm import load_llm
from rag.rag_chain import ask_question

from index import index_pdf, build_vector_database

from utils.file_manager import (
    get_uploaded_pdfs,
    delete_pdf
)

from utils.greetings import (
    is_greeting,
    greeting_response
)

from utils.source_utils import group_sources

from retriever.reranker import CrossEncoderReranker
from loaders.document_loader import SUPPORTED_EXTENSIONS


# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="📚",
    layout="wide"
)


# -------------------------------------------------------
# Startup: directory + env validation
# -------------------------------------------------------

ensure_uploads_dir()

env_errors = validate_env()

if env_errors:
    st.error("### ⚠️ Configuration Error\n\nThe following required settings are missing:\n\n" +
             "\n\n".join(f"- {e}" for e in env_errors))
    st.info("Add the missing values to your `.env` file and restart the app.")
    st.stop()


# -------------------------------------------------------
# Session State
# -------------------------------------------------------

if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

if "processed_upload" not in st.session_state:
    st.session_state.processed_upload = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------------------------------------
# Page Title
# -------------------------------------------------------

st.title("📚 RAG Chatbot")

st.write(
    "Ask questions from your uploaded documents."
)


# -------------------------------------------------------
# Load Models
# -------------------------------------------------------

@st.cache_resource
def load_models():

    try:
        embedding_model = load_embedding_model()
    except Exception as e:
        st.error(f"❌ Failed to load embedding model: {e}")
        st.stop()

    try:
        retriever = load_hybrid_retriever(embedding_model)
    except Exception as e:
        st.error(
            f"❌ Failed to connect to MongoDB Atlas or load retriever.\n\n"
            f"**Error:** {e}\n\n"
            "Check that your `MONGODB_ATLAS_URI` is correct and the "
            "cluster is reachable."
        )
        st.stop()

    try:
        llm = load_llm()
    except Exception as e:
        st.error(f"❌ Failed to load language model: {e}")
        st.stop()

    reranker = CrossEncoderReranker()

    return (
        embedding_model,
        retriever,
        llm,
        reranker
    )


(
    embedding_model,
    retriever,
    llm,
    reranker
) = load_models()


# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("📂 Document Management")

# Build accepted extension string for uploader
_accepted_exts = sorted(
    ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS
)

uploaded_file = st.sidebar.file_uploader(
    "Upload a document",
    type=_accepted_exts,
    help=f"Supported formats: {', '.join('.' + e for e in _accepted_exts)}"
)


# -------------------------------------------------------
# Reset Upload State
# -------------------------------------------------------

if uploaded_file is None:

    st.session_state.processed_upload = None


# -------------------------------------------------------
# Upload & Index Document
# -------------------------------------------------------

if uploaded_file is not None:

    if (
        uploaded_file.name
        != st.session_state.processed_upload
    ):

        save_path = os.path.join(
            "uploads",
            uploaded_file.name
        )

        # ---------------------------------------------
        # Duplicate check
        # ---------------------------------------------

        if os.path.exists(save_path):

            st.sidebar.warning(
                "⚠️ This document already exists."
            )

        else:

            # -----------------------------------------
            # Save file
            # -----------------------------------------

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.sidebar.success(
                f"'{uploaded_file.name}' uploaded successfully!"
            )

            # -----------------------------------------
            # Index document
            # -----------------------------------------

            with st.spinner(
                f"Indexing '{uploaded_file.name}'..."
            ):
                try:
                    index_pdf(save_path)

                    # Reload models with updated index
                    st.cache_resource.clear()

                    (
                        embedding_model,
                        retriever,
                        llm,
                        reranker
                    ) = load_models()

                    st.sidebar.success(
                        "✅ Document indexed successfully!"
                    )

                except ValueError as ve:
                    st.sidebar.error(
                        f"❌ Could not index '{uploaded_file.name}':\n\n{ve}"
                    )
                    # Remove the file so it doesn't appear in the list
                    os.remove(save_path)

                except Exception as e:
                    st.sidebar.error(
                        f"❌ Indexing failed: {e}"
                    )
                    os.remove(save_path)


        st.session_state.processed_upload = (
            uploaded_file.name
        )


# -------------------------------------------------------
# Uploaded Documents List
# -------------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader(
    "📄 Uploaded Documents"
)


pdfs = get_uploaded_pdfs()


if len(pdfs) == 0:

    st.sidebar.info(
        "No documents uploaded yet."
    )

else:

    for pdf in pdfs:

        col1, col2 = st.sidebar.columns(
            [4, 1]
        )


        with col1:

            st.write(
                f"📄 {pdf}"
            )


        with col2:

            if st.button(
                "❌",
                key=f"delete_{pdf}"
            ):

                try:
                    deleted_chunks = delete_pdf(
                        pdf,
                        embedding_model
                    )

                    # Reload retriever
                    st.cache_resource.clear()

                    (
                        embedding_model,
                        retriever,
                        llm,
                        reranker
                    ) = load_models()

                    st.success(
                        f"✅ '{pdf}' deleted "
                        f"({deleted_chunks} chunks removed)"
                    )

                except Exception as e:
                    st.error(f"❌ Could not delete '{pdf}': {e}")

                st.rerun()


# -------------------------------------------------------
# Database Status
# -------------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader(
    "📊 Database Status"
)


st.sidebar.write(
    f"Documents : {len(pdfs)}"
)


# -------------------------------------------------------
# Rebuild Database
# -------------------------------------------------------

if st.sidebar.button(
    "🔄 Rebuild Database"
):

    with st.spinner(
        "Rebuilding database..."
    ):

        try:
            st.cache_resource.clear()

            build_vector_database("uploads")

            (
                embedding_model,
                retriever,
                llm,
                reranker
            ) = load_models()

            st.sidebar.success(
                "✅ Database rebuilt successfully!"
            )

        except Exception as e:
            st.sidebar.error(f"❌ Rebuild failed: {e}")


# -------------------------------------------------------
# Clear Database
# -------------------------------------------------------

if st.sidebar.button(
    "🗑 Clear Database"
):

    try:
        from pymongo import MongoClient
        from config import MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

        uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_ATLAS_URI", "")
        db_name = os.getenv("DATABASE_NAME", MONGODB_DB_NAME)
        collection_name = os.getenv("COLLECTION_NAME", MONGODB_COLLECTION_NAME)
        if uri:
            client = MongoClient(uri)
            client[db_name][collection_name].delete_many({})

        st.cache_resource.clear()

        st.sidebar.success(
            "✅ Database cleared!"
        )

    except Exception as e:
        st.sidebar.error(f"❌ Could not clear database: {e}")


# =======================================================
# Helper: render sources with excerpts
# =======================================================

def _render_sources(sources: list) -> None:
    """Display grouped citations with filename, page, and text excerpt."""
    if not sources:
        return

    grouped_sources = group_sources(sources)

    if not grouped_sources:
        return

    st.markdown("### 📚 Sources")

    for file, entries in grouped_sources.items():

        st.markdown(f"📄 **{file}**")

        for entry in sorted(entries, key=lambda x: x["page"] or 0):

            page_label = (
                f"Page {entry['page']}"
                if entry["page"] is not None
                else "Page unknown"
            )

            excerpt = entry.get("excerpt", "").strip()

            if excerpt:
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;• **{page_label}**\n"
                    f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                    f"*\"{excerpt}\"*"
                )
            else:
                st.markdown(
                    f"&nbsp;&nbsp;&nbsp;• {page_label}"
                )


# =======================================================
# Display Previous Chat Messages
# =======================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):
            _render_sources(message["sources"])


# =======================================================
# Chat Input
# =======================================================

question = st.chat_input(
    "Ask a question..."
)


# =======================================================
# Ask Question
# =======================================================

if question:

    # ---------------------------------------------------
    # Save user message
    # ---------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # ---------------------------------------------------
    # Display user message
    # ---------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    # ---------------------------------------------------
    # Greeting
    # ---------------------------------------------------

    if is_greeting(question):

        answer = greeting_response(question)

        sources = []

        with st.chat_message("assistant"):

            st.markdown(answer)


    # ---------------------------------------------------
    # RAG Question
    # ---------------------------------------------------

    else:

        answer = ""

        sources = []

        with st.spinner("Thinking..."):

            try:
                for result in ask_question(
                    question,
                    st.session_state.messages,
                    retriever,
                    llm,
                    reranker
                ):

                    if result["type"] == "text":
                        answer += result["content"]

                    elif result["type"] == "sources":
                        sources = result["content"]

            except Exception as e:
                answer = (
                    "❌ An error occurred while generating the answer. "
                    "Please try again."
                )
                st.error(f"RAG pipeline error: {e}")

        with st.chat_message("assistant"):

            st.markdown(answer)

            _render_sources(sources)


    # ---------------------------------------------------
    # Save assistant message
    # ---------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )