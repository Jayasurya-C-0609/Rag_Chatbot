"""
Unified document loader.

Supports: PDF (.pdf), Word (.docx), plain-text (.txt), CSV (.csv).
All loaders return a list of LangChain ``Document`` objects with
``source`` and ``page`` metadata fields set consistently.
"""

import os
from pathlib import Path

from langchain_community.document_loaders import (
    PyMuPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
)


# Map file extension → LangChain loader class
_EXTENSION_MAP = {
    ".pdf":  PyMuPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt":  TextLoader,
    ".csv":  CSVLoader,
}

SUPPORTED_EXTENSIONS = set(_EXTENSION_MAP.keys())


def load_file(file_path: str) -> list:
    """
    Load a single file. Returns a list of Document objects.
    Raises ``ValueError`` for unsupported extensions.
    """
    ext = Path(file_path).suffix.lower()
    loader_cls = _EXTENSION_MAP.get(ext)

    if loader_cls is None:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    loader = loader_cls(file_path)
    docs = loader.load()

    # ----------------------------------------------------------
    # Normalise metadata: ensure 'source' is always set and
    # ensure 'page' defaults to 0 for loaders that omit it.
    # ----------------------------------------------------------
    for i, doc in enumerate(docs):
        doc.metadata.setdefault("source", file_path)
        if "page" not in doc.metadata:
            doc.metadata["page"] = i  # use doc index as page fallback

    return docs


def load_documents(folder: str) -> list:
    """
    Recursively load all supported documents from ``folder``.

    Files with unsupported extensions are silently skipped.
    Any per-file error is printed as a warning and the file is skipped
    so that one bad file doesn't abort the whole ingestion.
    """
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"⚠️  Folder '{folder}' does not exist. Returning empty list.")
        return []

    all_docs = []

    for file_path in sorted(folder_path.iterdir()):
        ext = file_path.suffix.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            continue

        try:
            docs = load_file(str(file_path))
            all_docs.extend(docs)
            print(
                f"  [OK] Loaded {len(docs)} page(s) from "
                f"'{file_path.name}'"
            )
        except Exception as exc:
            print(
                f"  [WARN] Could not load '{file_path.name}': {exc}"
            )

    return all_docs
