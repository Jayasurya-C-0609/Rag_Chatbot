"""
PDF-specific loader (backward-compatibility shim).

Internally delegates to ``document_loader.load_documents`` with
PyMuPDFLoader for richer text extraction, better layout handling,
and metadata (page numbers, author, title) compared to PyPDFLoader.
"""

from loaders.document_loader import load_documents


def load_pdfs(data_folder: str) -> list:
    """
    Load all PDF files from ``data_folder`` using PyMuPDF.

    Non-PDF files in the folder are ignored.
    Returns a list of LangChain Document objects.
    """
    from pathlib import Path
    from langchain_community.document_loaders import PyMuPDFLoader

    folder_path = Path(data_folder)
    if not folder_path.exists():
        return []

    documents = []
    for pdf_file in sorted(folder_path.glob("*.pdf")):
        try:
            loader = PyMuPDFLoader(str(pdf_file))
            docs = loader.load()
            # Ensure page metadata is present
            for i, doc in enumerate(docs):
                doc.metadata.setdefault("source", str(pdf_file))
                doc.metadata.setdefault("page", i)
            documents.extend(docs)
        except Exception as exc:
            print(f"⚠️  Could not load '{pdf_file.name}': {exc}")

    return documents