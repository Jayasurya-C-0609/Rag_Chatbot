import os
import shutil
import streamlit as st

from embeddings.embedding_model import load_embedding_model
from retriever.hybrid_retriever import load_hybrid_retriever
from llm.llm import load_llm
from rag.rag_chain import ask_question

from index import index_file, build_vector_database

from utils.file_manager import (
    get_uploaded_files,
    delete_file
)

from utils.greetings import (
    is_greeting,
    greeting_response
)

from utils.source_utils import group_sources

from retriever.reranker import CrossEncoderReranker


# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="📚",
    layout="wide"
)


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

    embedding_model = load_embedding_model()

    retriever = load_hybrid_retriever(
        embedding_model
    )

    llm = load_llm()

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


uploaded_files = st.sidebar.file_uploader(
    "Upload documents",
    type=[
        "pdf",
        "txt",
        "csv",
        "xlsx",
        "xls",
        "docx",
        "pptx"
    ],
    accept_multiple_files=True
)


# -------------------------------------------------------
# Reset Upload State
# -------------------------------------------------------

if not uploaded_files:

    st.session_state.processed_upload = []


# -------------------------------------------------------
# Upload Documents
# -------------------------------------------------------

if uploaded_files:

    for uploaded_file in uploaded_files:

        filename = uploaded_file.name

        # ---------------------------------------------
        # Skip already processed file
        # ---------------------------------------------

        if filename in st.session_state.processed_upload:
            continue


        save_path = os.path.join(
            "uploads",
            filename
        )


        # ---------------------------------------------
        # Duplicate check
        # ---------------------------------------------

        if os.path.exists(save_path):

            st.sidebar.warning(
                f"⚠️ {filename} already exists."
            )

            st.session_state.processed_upload.append(
                filename
            )

            continue


        # ---------------------------------------------
        # Save file
        # ---------------------------------------------

        with open(
            save_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )


        st.sidebar.success(
            f"✅ {filename} uploaded successfully!"
        )


        # ---------------------------------------------
        # Index file
        # ---------------------------------------------

        with st.spinner(
            f"Indexing {filename}..."
        ):

            index_file(
                save_path
            )


        # ---------------------------------------------
        # Mark as processed
        # ---------------------------------------------

        st.session_state.processed_upload.append(
            filename
        )


    # ---------------------------------------------
    # Reload models once after all files
    # ---------------------------------------------

    st.cache_resource.clear()

    (
        embedding_model,
        retriever,
        llm,
        reranker
    ) = load_models()


    st.sidebar.success(
        "✅ Vector Database Updated!"
    )


# -------------------------------------------------------
# Uploaded Documents
# -------------------------------------------------------

st.sidebar.divider()

st.sidebar.subheader(
    "📄 Uploaded Documents"
)


pdfs = get_uploaded_files()


if len(pdfs) == 0:

    st.sidebar.info(
        "No files uploaded."
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

                deleted_chunks = delete_file(
                    pdf,
                    embedding_model
                )


                # -------------------------------------
                # Reload retriever
                # -------------------------------------

                st.cache_resource.clear()

                (
                    embedding_model,
                    retriever,
                    llm,
                    reranker
                ) = load_models()


                st.success(
                    f"✅ {pdf} deleted "
                    f"({deleted_chunks} chunks removed)"
                )


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

        st.cache_resource.clear()

        build_vector_database(
            "uploads"
        )


        (
            embedding_model,
            retriever,
            llm,
            reranker
        ) = load_models()


    st.sidebar.success(
        "✅ Database rebuilt successfully!"
    )


# -------------------------------------------------------
# Clear Database
# -------------------------------------------------------

if st.sidebar.button(
    "🗑 Clear Database"
):

    if os.path.exists(
        "chroma_db"
    ):

        shutil.rmtree(
            "chroma_db"
        )


    st.cache_resource.clear()


    st.sidebar.success(
        "✅ Database cleared!"
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


        # ---------------------------------------------
        # Display sources
        # ---------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            grouped_sources = group_sources(
                message["sources"]
            )


            if grouped_sources:

                st.markdown(
                    "### 📚 Sources"
                )


                for file, pages in (
                    grouped_sources.items()
                ):

                    st.markdown(
                        f"📄 **{file}**"
                    )


                    for page in sorted(
                        pages
                    ):

                        st.markdown(
                            f"&nbsp;&nbsp;&nbsp;• "
                            f"Page {page}"
                        )


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

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # ---------------------------------------------------
    # Greeting
    # ---------------------------------------------------

    if is_greeting(
        question
    ):

        answer = greeting_response(
            question
        )

        sources = []


        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                answer
            )


    # ---------------------------------------------------
    # RAG Question
    # ---------------------------------------------------

    else:

        answer = ""

        sources = []


        # ---------------------------------------------
        # Run RAG ONLY ONCE
        # ---------------------------------------------

        with st.spinner(
            "Thinking..."
        ):

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


        # ---------------------------------------------
        # Display complete assistant response ONCE
        # ---------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                answer
            )


            # -----------------------------------------
            # Display sources ONCE
            # -----------------------------------------

            if sources:

                grouped_sources = group_sources(
                    sources
                )


                if grouped_sources:

                    st.markdown(
                        "### 📚 Sources"
                    )


                    for file, pages in (
                        grouped_sources.items()
                    ):

                        st.markdown(
                            f"📄 **{file}**"
                        )


                        for page in sorted(
                            pages
                        ):

                            st.markdown(
                                f"&nbsp;&nbsp;&nbsp;• "
                                f"Page {page}"
                            )


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