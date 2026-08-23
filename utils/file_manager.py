import os

from vectordb.delete_documents import delete_document
from loaders.document_loader import SUPPORTED_EXTENSIONS

UPLOAD_FOLDER = "uploads"


def get_uploaded_pdfs():
    """
    Return a sorted list of all supported documents in the upload folder.
    Despite the legacy name, this now returns all supported file types.
    """
    if not os.path.exists(UPLOAD_FOLDER):
        return []

    files = [
        file
        for file in os.listdir(UPLOAD_FOLDER)
        if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS
    ]

    return sorted(files)


def delete_pdf(filename, embedding_model):
    """
    Delete a document's vectors from MongoDB and remove it from disk.
    Despite the legacy name, works for any supported file type.
    """
    # Delete vectors from MongoDB Atlas
    deleted_chunks = delete_document(
        filename,
        embedding_model
    )

    # Delete file from disk
    path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.exists(path):
        os.remove(path)

    return deleted_chunks