<div align="center">
  <h1>🧠 ContextIQ</h1>
  <p><strong>AI-Powered Knowledge Assistant & Document RAG Platform</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb&logoColor=white" alt="MongoDB Atlas" />
    <img src="https://img.shields.io/badge/LangChain-121212?style=flat&logo=chainlink" alt="LangChain" />
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black" alt="Vanilla JS" />
  </p>
</div>

---

## 📖 Overview

**ContextIQ** is an advanced, production-ready **Retrieval-Augmented Generation (RAG)** chatbot. It empowers users to upload PDF documents and ask natural language questions grounded *strictly* in the provided knowledge base. 

Unlike generic chatbots, ContextIQ strictly enforces **Document Grounding**: it will explicitly cite the file and page number from which it derived its answer. If the answer cannot be found in the uploaded documents, it is designed to transparently abstain by responding, *"I don't know based on the provided documents."*

The platform features a high-performance **FastAPI backend**, an elegant **Vanilla JavaScript frontend**, and a robust **Hybrid Search** retrieval pipeline powered by **MongoDB Atlas Vector Search**.

---

## ✨ Key Features

### 🖥️ Modern Web Interface
- **Pure Vanilla Stack:** Beautiful, responsive UI built entirely with HTML5, CSS3, and Vanilla JavaScript—no heavy frameworks required.
- **Dynamic Streaming:** Real-time AI responses utilizing Server-Sent Events (SSE), complete with loading states and token-by-token rendering.
- **Integrated Workspace:** Seamlessly switch between the conversational Chat interface and the Knowledge Base management dashboard.
- **Precise Citations:** AI responses explicitly highlight the original PDF files and exact pages they derived their answers from.

### 🧠 Advanced RAG Pipeline
- **Hybrid Retrieval:** Combines the contextual understanding of Semantic Vector Search with the precise exact-match capabilities of Lexical Search (BM25) for maximum recall.
- **Cross-Encoder Reranking:** Dynamically re-scores and re-ranks retrieved chunks using `cross-encoder/ms-marco-MiniLM-L-6-v2` to ensure only the most highly relevant context reaches the LLM.
- **Strict Grounding:** The LLM is explicitly prompt-engineered to prevent hallucination outside the provided context.
- **Context-Aware Follow-ups:** Automatically rewrites follow-up questions into standalone queries by analyzing the conversation history, enabling seamless conversational flows.

---

## 🏗️ High-Level Architecture & Flow

ContextIQ is divided into two primary pipelines: **Data Ingestion** (when a user uploads a document) and **Query Retrieval** (when a user asks a question).

### System Flow Diagram

```mermaid
flowchart TD
    %% Styling
    classDef frontend fill:#f7df1e,stroke:#333,stroke-width:2px,color:#000
    classDef backend fill:#005571,stroke:#333,stroke-width:2px,color:#fff
    classDef database fill:#4ea94b,stroke:#333,stroke-width:2px,color:#fff
    classDef model fill:#ff9900,stroke:#333,stroke-width:2px,color:#000
    classDef default fill:#f4f4f4,stroke:#333,stroke-width:1px,color:#333

    subgraph Frontend["🌐 Frontend Client (Browser)"]
        UI_KB[Knowledge Base UI]:::frontend
        UI_Chat[Workspace Chat UI]:::frontend
    end

    subgraph Backend["⚙️ FastAPI Backend Server"]
        API_Docs[/api/v1/documents]:::backend
        API_Chat[/api/v1/chat/stream]:::backend
        
        subgraph IngestionPipeline["📥 Data Ingestion Pipeline"]
            PyPDF[PyPDF Loader]
            Splitter[Recursive Text Splitter]
            Embeddings1[Embedding Model<br/>bge-small-en]:::model
        end
        
        subgraph QueryPipeline["🔍 Query & Retrieval Pipeline"]
            QueryRewriter[Query Rewriter LLM]:::model
            HybridSearch[Hybrid Retriever<br/>Semantic + BM25]
            Reranker[Cross-Encoder Reranker<br/>ms-marco-MiniLM]:::model
            Embeddings2[Embedding Model<br/>bge-small-en]:::model
            FinalLLM[Groq LLM<br/>gpt-oss-20b]:::model
        end
    end

    subgraph Database["🗄️ MongoDB Atlas"]
        MongoVS[(Vector Search Index)]:::database
    end

    %% Ingestion Flow
    UI_KB -- "Upload PDF" --> API_Docs
    API_Docs --> PyPDF
    PyPDF -- "Extract Text" --> Splitter
    Splitter -- "Chunks" --> Embeddings1
    Embeddings1 -- "Vectors & Metadata" --> MongoVS

    %% Chat Flow
    UI_Chat -- "Ask Question" --> API_Chat
    API_Chat --> QueryRewriter
    QueryRewriter -- "Standalone Query" --> Embeddings2
    Embeddings2 -- "Query Vector" --> HybridSearch
    
    HybridSearch -- "Search" --> MongoVS
    MongoVS -- "Top Candidates" --> HybridSearch
    
    HybridSearch -- "Initial Chunks" --> Reranker
    Reranker -- "Strictly Reranked Top 8" --> FinalLLM
    
    FinalLLM -- "SSE Stream" --> API_Chat
    API_Chat -. "Stream" .-> UI_Chat
```

### Detailed Pipeline Breakdown

1. **Ingestion (Document Loading & Chunking):** 
   PDFs are parsed using `PyPDFLoader` and split into smaller, manageable chunks using a `RecursiveCharacterTextSplitter` (1,000-character chunks with a 100-character overlap to preserve context across boundaries).
2. **Embedding:** 
   Chunks are converted into dense vector embeddings using the local HuggingFace model `BAAI/bge-small-en-v1.5`.
3. **Persistent Storage:** 
   The vectors, along with essential metadata (filename, page number, raw text), are securely stored in **MongoDB Atlas**.
4. **Query Rewriting:** 
   When a user asks a follow-up question (e.g., "What happens if they don't meet it?"), the system uses the LLM to rewrite it into a standalone query (e.g., "What happens if students do not meet the 75% attendance requirement?") using the chat history.
5. **Hybrid Retrieval:** 
   The standalone query searches MongoDB Atlas using a Hybrid Search approach, retrieving a broad set of candidate chunks.
6. **Cross-Encoder Reranking:** 
   The broad candidate chunks are deeply evaluated against the query using a Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) to strictly sort them by actual relevance. The top 8 most relevant chunks are selected.
7. **Grounded Generation:** 
   The top 8 chunks are fed to the Groq LLM with a strict system prompt to generate the final answer and stream it back to the client via Server-Sent Events (SSE).

---

## 🛠️ Technology Stack

| Category | Technologies Used | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JS | A zero-dependency, lightweight, and blazing-fast user interface. |
| **Backend API** | FastAPI, Uvicorn, Python 3.10+ | Asynchronous backend framework handling routes, streaming, and business logic. |
| **LLM Inference** | Groq API (`openai/gpt-oss-20b`) | Ultra-fast inference engine used for both query rewriting and final answer generation. |
| **Embeddings** | HuggingFace (`BAAI/bge-small-en-v1.5`) | Local, high-performance embedding model used to vectorize documents and queries. |
| **Reranking** | HuggingFace (`cross-encoder/ms-marco-MiniLM-L-6-v2`) | Local cross-encoder model used to score the relevance of retrieved chunks. |
| **Database** | MongoDB Atlas (Vector Search) | Cloud-native NoSQL database acting as the primary persistent vector store. |
| **Orchestration**| LangChain | Framework used to wire together the loaders, splitters, retrievers, and LLMs. |
| **Tooling** | `uv`, `pytest` | Extremely fast Python package manager and testing framework. |

---

## 🚀 Setup & Installation Guide

Follow these steps to set up ContextIQ locally.

### Prerequisites
- **Python 3.10** or higher installed.
- **[uv](https://github.com/astral-sh/uv)** installed globally (Recommended for fast dependency management).
- A **[Groq API Key](https://console.groq.com/)** for LLM inference.
- A **[MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database)** cluster with a configured Vector Search index.

### 1. Clone the Repository

```bash
git clone https://github.com/Karthick-564/Team_Qernels.git
cd Team_Qernels/Rag_Chatbot
```

### 2. Install Dependencies

Using `uv` for lightning-fast environment creation and syncing:

```bash
uv sync
```
*(Alternatively, you can use standard `pip install -r requirements.txt` if you prefer).*

### 3. Environment Configuration

Create a `.env` file in the root directory of the project (`Rag_Chatbot/.env`). Copy the following template and fill in your credentials:

```dotenv
# === LLM Configuration ===
# Get your API key from https://console.groq.com/keys
GROQ_API_KEY="your_groq_api_key_here"

# === MongoDB Atlas Configuration ===
# Replace <username>, <password>, and <cluster> with your Atlas details.
MONGODB_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=Rag"
DATABASE_NAME="rag_db"
COLLECTION_NAME="test"
```

*Note: Ensure your MongoDB Atlas collection has a Vector Search Index configured for the embeddings to work correctly.*

### 4. Start the Application

The FastAPI backend is designed to serve both the REST API and the Frontend static files simultaneously. You only need to run one command from the project root:

```bash
uv run uvicorn backend.main:app --reload --port 8000
```
*(Note: The first time you run this, it will download the HuggingFace Embedding and Reranker models, which may take a few moments depending on your internet connection).*

---

## 💡 How to Use ContextIQ

Once the server indicates `Application startup complete`, open your web browser and navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

### Step 1: Manage Knowledge Base
1. Click the hamburger menu (sidebar) and select **Knowledge Base**.
2. Click the upload zone or drag-and-drop a **PDF document** into the area.
3. Wait for the file to upload and process. The UI will indicate when it is "Indexed & Ready".
4. *(Optional)* You can manage existing documents here, including deleting specific files or clearing the entire database.

### Step 2: Chat in the Workspace
1. Open the sidebar and select **Workspace**.
2. Type a question related to the PDF you just uploaded into the chat bar at the bottom.
3. Press **Enter** or click the send arrow.
4. Watch as the AI streams its answer in real-time, followed by the exact file and page citations it used to ground its response!
5. Ask follow-up questions naturally; the system will remember the context of your conversation.

---

## 🧪 Testing & Evaluation

The repository includes a comprehensive `pytest` suite for backend validation and end-to-end integration tests.

```bash
# Run all automated tests
uv run pytest backend/tests/ -v
```

### LLM Evaluation
ContextIQ includes scripts to evaluate retrieval precision, recall, answer faithfulness, and abstention logic using the RAGAS framework:
```bash
python evaluation/run_rag_test.py
python evaluation/ragas_evaluation.py
```

---

## 🔒 Security & Safety Features

ContextIQ is built with security and reliability in mind:
- **Path Traversal Protection:** All document file paths are actively sanitized on upload and deletion endpoints to prevent malicious directory traversal.
- **Exception Sanitization:** Global exception handlers prevent internal stack traces, environment variables, or database connection URIs from leaking to the frontend in the event of an error.
- **Prompt Isolation Constraints:** The LLM is strictly constrained via system prompts to prevent hallucination and outside-knowledge leakage.

---

## 👨‍💻 Project Directory Structure

```text
Rag_Chatbot/
├── backend/                   # FastAPI backend architecture
│   ├── api/routes/            # REST Endpoints (chat, documents, health)
│   ├── core/                  # App Configuration & Logging setup
│   ├── schemas/               # Pydantic validation models for I/O
│   ├── services/              # Business logic (System, Chat, Indexing)
│   ├── tests/                 # Comprehensive Pytest suite
│   └── main.py                # FastAPI app entry point & Static mounting
├── frontend/                  # Vanilla JS Web UI
│   ├── css/styles.css         # Modern, responsive CSS styling
│   ├── js/app.js              # State management & SSE stream parsing
│   ├── index.html             # Landing page
│   ├── workspace.html         # Chat interface
│   └── knowledge-base.html    # Document management dashboard
├── rag/                       # Core RAG logic & LLM Prompt Templates
├── retriever/                 # Hybrid search logic & Cross-Encoder reranker
├── embeddings/                # Local HuggingFace embedding initialization
├── llm/                       # Groq LLM client integration
├── vectordb/                  # MongoDB Atlas CRUD operations
├── loaders/                   # PyPDF document parsing
├── preprocess/                # Recursive character text chunking
├── utils/                     # Helpers (e.g., source extraction)
├── evaluation/                # RAGAS metric evaluation scripts
├── uploads/                   # Temporary directory for file uploads
├── .env                       # Environment variables (ignored by Git)
├── uv.lock                    # Dependency lockfile
└── pyproject.toml             # Project metadata & dependencies
```
