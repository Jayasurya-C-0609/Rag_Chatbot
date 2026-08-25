import os
import shutil
import streamlit as st


# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="📚",
    layout="wide"
)


# -------------------------------------------------------
# Imports
# -------------------------------------------------------

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


# =======================================================
# CUSTOM CSS
# =======================================================
st.markdown("""
<style>

/* ================= APP ================= */

.stApp {
    background: #F8FAFC;
}


/* ================= MAIN HEADER ================= */

.main-header {
    font-size: 40px !important;
    font-weight: 700 !important;
    color: #0F172A !important;
}

.subtitle {
    font-size: 16px !important;
    color: #64748B !important;
}


/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: #0F172A !important;
}


/* Document Management */

.sidebar-title {
    color: #FFFFFF !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    white-space: nowrap !important;
    margin-bottom: 18px !important;
}


/* Uploaded Documents */

.uploaded-title {
    color: #FFFFFF !important;
    font-size: 19px !important;
    font-weight: 600 !important;
    margin-bottom: 15px !important;
}

.document-name {
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 500 !important;
}


/* Database */

.database-title {
    color: #FFFFFF !important;
    font-size: 19px !important;
    font-weight: 600 !important;
}

.document-count {
    color: #FFFFFF !important;
    font-size: 17px !important;
}


/* ================= FILE UPLOADER ================= */

section[data-testid="stSidebar"]
[data-testid="stFileUploader"] {
    background: #FFFFFF !important;
    border: 1px dashed #94A3B8 !important;
    border-radius: 12px !important;
    padding: 10px !important;
}


/* Upload label */

section[data-testid="stFileUploader"] label {
    color: #334155 !important;
    opacity: 1 !important;
}


/* Upload button */

section[data-testid="stFileUploader"] button {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #94A3B8 !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    transition: 0.2s !important;
}

section[data-testid="stFileUploader"] button span,
section[data-testid="stFileUploader"] button p,
section[data-testid="stFileUploader"] button svg {
    color: #0F172A !important;
    stroke: #0F172A !important;
    fill: none !important;
    opacity: 1 !important;
}


/* Upload hover */

section[data-testid="stFileUploader"] button:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
}

section[data-testid="stFileUploader"] button:hover span,
section[data-testid="stFileUploader"] button:hover p,
section[data-testid="stFileUploader"] button:hover svg {
    color: #2563EB !important;
    stroke: #2563EB !important;
}


/* Supported formats */

section[data-testid="stFileUploader"] small {
    color: #475569 !important;
    opacity: 1 !important;
}


/* ================= SIDEBAR BUTTONS ================= */

section[data-testid="stSidebar"] .stButton > button {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    transition: 0.2s !important;
}

section[data-testid="stSidebar"] .stButton > button span,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button svg {
    color: #0F172A !important;
    stroke: #0F172A !important;
    opacity: 1 !important;
}


/* Sidebar button hover */

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
}

section[data-testid="stSidebar"] .stButton > button:hover span,
section[data-testid="stSidebar"] .stButton > button:hover p,
section[data-testid="stSidebar"] .stButton > button:hover svg {
    color: #2563EB !important;
    stroke: #2563EB !important;
}


/* ================= COLLAPSE BUTTON ================= */

/* Open sidebar: << */

[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
}

[data-testid="stSidebarCollapseButton"] svg {
    color: #0F172A !important;
    stroke: #0F172A !important;
    fill: none !important;
    opacity: 1 !important;
}

[data-testid="stSidebarCollapseButton"]:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
}

[data-testid="stSidebarCollapseButton"]:hover svg {
    color: #2563EB !important;
    stroke: #2563EB !important;
}


/* Collapsed sidebar: >> */

[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

[data-testid="collapsedControl"] button {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 10px !important;
}

[data-testid="collapsedControl"] svg {
    color: #0F172A !important;
    stroke: #0F172A !important;
    fill: none !important;
}

[data-testid="collapsedControl"] button:hover {
    background: #EFF6FF !important;
    border-color: #2563EB !important;
}


/* ================= CHAT ================= */

[data-testid="stChatMessage"] {
    border-radius: 12px !important;
    padding: 10px !important;
    margin-bottom: 10px !important;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {
    background: #DBEAFE !important;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
}


/* ================= SOURCES ================= */

.source-card {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    padding: 12px 15px !important;
}

.source-title {
    color: #0F172A !important;
    font-weight: 600 !important;
}

.source-page {
    color: #64748B !important;
    font-size: 13px !important;
}


/* ================= CHAT INPUT ================= */

.stChatInput {
    border-radius: 12px !important;
}

/* Chat input text */
[data-testid="stChatInput"] textarea {
    font-size: 16px !important;
}

/* Chat input placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    font-size: 16px !important;
    color: #64748B !important;
}


/* ================= DIVIDER ================= */

hr {
    border-color: #E2E8F0 !important;
}

</style>
""", unsafe_allow_html=True)
# =======================================================
# SESSION STATE
# =======================================================

if "last_uploaded" not in st.session_state:
    st.session_state.last_uploaded = None

if "processed_upload" not in st.session_state:
    st.session_state.processed_upload = []

if "messages" not in st.session_state:
    st.session_state.messages = []


# =======================================================
# PAGE TITLE
# =======================================================

st.markdown(
    '<div class="main-header">📚 RAG Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ask questions from your uploaded documents.</div>',
    unsafe_allow_html=True
)


# =======================================================
# LOAD EXPENSIVE MODELS
# =======================================================

@st.cache_resource
def load_models():

    embedding_model = load_embedding_model()

    llm = load_llm()

    reranker = CrossEncoderReranker()

    return (
        embedding_model,
        llm,
        reranker
    )


# =======================================================
# LOAD RETRIEVER SEPARATELY
# =======================================================

@st.cache_resource
def load_retriever(embedding_model):

    return load_hybrid_retriever(
        embedding_model
    )


# =======================================================
# LOAD MODELS
# =======================================================

(
    embedding_model,
    llm,
    reranker
) = load_models()


# =======================================================
# LOAD RETRIEVER
# =======================================================

retriever = load_retriever(
    embedding_model
)


# =======================================================
# SIDEBAR
# =======================================================

st.sidebar.markdown(
    '<div class="sidebar-title">📁 Document Management</div>',
    unsafe_allow_html=True
)


# =======================================================
# FILE UPLOAD
# =======================================================

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


# =======================================================
# UPLOAD DOCUMENTS
# =======================================================

new_file_uploaded = False


if uploaded_files:

    for uploaded_file in uploaded_files:

        filename = uploaded_file.name

        # -----------------------------------------------
        # Already processed
        # -----------------------------------------------

        if filename in st.session_state.processed_upload:
            continue


        save_path = os.path.join(
            "uploads",
            filename
        )


        # -----------------------------------------------
        # Duplicate file
        # -----------------------------------------------

        if os.path.exists(save_path):

            st.sidebar.warning(
                f"⚠️ {filename} already exists."
            )

            st.session_state.processed_upload.append(
                filename
            )

            continue


        # -----------------------------------------------
        # Save file
        # -----------------------------------------------

        with open(
            save_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )


        # -----------------------------------------------
        # Index file
        # -----------------------------------------------

        with st.spinner(
            f"Indexing {filename}..."
        ):

            index_file(
                save_path
            )


        # -----------------------------------------------
        # Mark processed
        # -----------------------------------------------

        st.session_state.processed_upload.append(
            filename
        )

        new_file_uploaded = True


# =======================================================
# UPDATE RETRIEVER ONLY
# =======================================================

if new_file_uploaded:

    # Clear ONLY the retriever cache
    load_retriever.clear()

    # Rebuild retriever using the existing
    # embedding model
    retriever = load_retriever(
        embedding_model
    )

    st.sidebar.success(
        "✅ Vector Database Updated!"
    )


# =======================================================
# UPLOADED DOCUMENTS
# =======================================================

st.sidebar.divider()

st.sidebar.markdown(
    '<div class="uploaded-title">📄 Uploaded Documents</div>',
    unsafe_allow_html=True
)


pdfs = get_uploaded_files()


if len(pdfs) == 0:

    st.sidebar.info(
        "No files uploaded."
    )

else:

    for pdf in pdfs:

        col1, col2 = st.sidebar.columns(
            [5, 1]
        )


        # -----------------------------------------------
        # Document name
        # -----------------------------------------------

        with col1:

            st.markdown(
                f'<div class="document-name">📄 {pdf}</div>',
                unsafe_allow_html=True
            )


        # -----------------------------------------------
        # Delete button
        # -----------------------------------------------

        with col2:

            delete_clicked = st.button(
                "❌",
                key=f"delete_{pdf}"
            )


        # -----------------------------------------------
        # Delete outside narrow column
        # -----------------------------------------------

        if delete_clicked:

            with st.spinner(
                f"Deleting {pdf}..."
            ):

                deleted_chunks = delete_file(
                    pdf,
                    embedding_model
                )


                # Clear ONLY retriever
                load_retriever.clear()


                # Rebuild retriever
                retriever = load_retriever(
                    embedding_model
                )


            st.sidebar.success(
                f"✅ {pdf} deleted "
                f"({deleted_chunks} chunks removed)"
            )

            st.rerun()


# =======================================================
# DATABASE STATUS
# =======================================================

st.sidebar.divider()

st.sidebar.markdown(
    '<div class="database-title">📊 Database Status</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown(
    f'<div class="document-count">Documents: {len(pdfs)}</div>',
    unsafe_allow_html=True
)


# =======================================================
# REBUILD DATABASE
# =======================================================

if st.sidebar.button(
    "🔄 Rebuild Database"
):

    with st.spinner(
        "Rebuilding database..."
    ):

        build_vector_database(
            "uploads"
        )


        # Clear ONLY retriever
        load_retriever.clear()


        # Rebuild retriever
        retriever = load_retriever(
            embedding_model
        )


    st.sidebar.success(
        "✅ Database rebuilt successfully!"
    )


# =======================================================
# CLEAR DATABASE
# =======================================================

if st.sidebar.button(
    "🗑 Clear Database"
):

    if os.path.exists(
        "chroma_db"
    ):

        shutil.rmtree(
            "chroma_db"
        )


    # Clear ONLY retriever
    load_retriever.clear()


    # Reset retriever
    retriever = load_retriever(
        embedding_model
    )


    st.sidebar.success(
        "✅ Database cleared!" 
    )


# =======================================================
# DISPLAY PREVIOUS CHAT MESSAGES
# =======================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


        # -----------------------------------------------
        # Sources
        # -----------------------------------------------

        if (
            message["role"] == "assistant"
            and message.get("sources")):

            grouped_sources = group_sources(
                message["sources"]
            )

            if grouped_sources:

                st.markdown("### 📚 Sources")

                for file, pages in grouped_sources.items():

                    with st.expander(
                        f"📄 {file}"
                    ):

                        if pages:

                            st.markdown(
                                "**Pages:** "
                                + ", ".join(
                                    str(page)
                                    for page in sorted(pages)
                                )
                            )

                        else:

                            st.markdown(
                                "*Page information unavailable.*"
                            )


# =======================================================
# CHAT INPUT
# =======================================================

question = st.chat_input(
    "Ask a question..."
)


# =======================================================
# ASK QUESTION
# =======================================================

if question:

    # -----------------------------------------------
    # Save user message
    # -----------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # -----------------------------------------------
    # Display user message
    # -----------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    # ===================================================
    # GREETING
    # ===================================================

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


    # ===================================================
    # RAG QUESTION
    # ===================================================

    else:

        answer = ""

        sources = []


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


        # -----------------------------------------------
        # Display assistant response
        # -----------------------------------------------

        with st.chat_message(
            "assistant"
        ):

            st.markdown(
                answer
            )


            # -----------------------------------------------
            # Sources
            # -----------------------------------------------

            if sources:

                grouped_sources = group_sources(
                    sources
                )

                if grouped_sources:

                    st.markdown(
                        "### 📚 Sources"
                    )

                    for file, pages in grouped_sources.items():

                        with st.expander(
                            f"📄 {file}",
                            expanded=False
                        ):

                            if pages:

                                st.markdown(
                                    "**Pages:** "
                                    + ", ".join(
                                        str(page)
                                        for page in sorted(pages)
                                    )
                                )

                            else:

                                st.markdown(
                                    "*Page information unavailable.*"
                                )

    # ===================================================
    # SAVE ASSISTANT MESSAGE
    # ===================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources
        }
    )