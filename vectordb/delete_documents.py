import os

from dotenv import load_dotenv
from pymongo import MongoClient

from config import (
    MONGODB_DB_NAME,
    MONGODB_COLLECTION_NAME,
)

load_dotenv()


def delete_document(pdf_name, embedding_model=None):
    """
    Delete all chunks belonging to a PDF from MongoDB Atlas.

    Parameters
    ----------
    pdf_name : str
        The bare filename (e.g. "report.pdf") — matched against
        the ``source`` metadata field stored in each document.
    embedding_model : ignored
        Kept for API compatibility with old Chroma version.

    Returns
    -------
    int
        Number of deleted chunks.
    """
    uri = os.getenv("MONGODB_URI") or os.getenv("MONGODB_ATLAS_URI")
    if not uri:
        raise EnvironmentError(
            "MONGODB_URI is not set. "
            "Add it to your .env file."
        )

    db_name = os.getenv("DATABASE_NAME", MONGODB_DB_NAME)
    collection_name = os.getenv("COLLECTION_NAME", MONGODB_COLLECTION_NAME)

    client = MongoClient(uri)
    collection = client[db_name][collection_name]

    # Chunks store metadata as nested dict: {"source": "/path/to/file.pdf", ...}
    # We match on the trailing filename so it works regardless of upload path.
    result = collection.delete_many(
        {"metadata.source": {"$regex": pdf_name.replace(".", r"\.")}}
    )

    deleted_count = result.deleted_count
    print(
        f"Deleted {deleted_count} chunks for '{pdf_name}' "
        "from MongoDB Atlas."
    )
    return deleted_count