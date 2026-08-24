import os

from vectordb.delete_documents import delete_document
from config import UPLOAD_FOLDER


def get_uploaded_files():

    if not os.path.exists(UPLOAD_FOLDER):
        return []

    return [
        filename
        for filename in os.listdir(UPLOAD_FOLDER)
        if os.path.isfile(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )
    ]


def delete_file(filename, embedding_model):

    # Delete vectors from ChromaDB
    deleted_chunks = delete_document(
        filename,
        embedding_model
    )

    # Delete uploaded file
    path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.exists(path):
        os.remove(path)

    return deleted_chunks