import os

from langchain_chroma import Chroma

from config import CHROMA_DB_DIR


def delete_document(
    filename,
    embedding_model
):

    vector_store = Chroma(
        persist_directory=CHROMA_DB_DIR,
        embedding_function=embedding_model
    )

    data = vector_store.get(
        include=["metadatas"]
    )

    target = os.path.basename(
        filename
    ).lower()

    ids_to_delete = []

    for doc_id, metadata in zip(
        data["ids"],
        data["metadatas"]
    ):

        if not metadata:
            continue

        source = str(
            metadata.get(
                "source",
                ""
            )
        )

        source_name = os.path.basename(
            source
        ).lower()

        if source_name == target:
            ids_to_delete.append(
                doc_id
            )

    if ids_to_delete:

        vector_store.delete(
            ids=ids_to_delete
        )

    print(
        f"Deleted {len(ids_to_delete)} chunks "
        f"for {filename}"
    )

    return len(ids_to_delete)