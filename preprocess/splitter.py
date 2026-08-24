import os

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    final_chunks = []

    for document_index, document in enumerate(documents):

        source = document.metadata.get(
            "source",
            "unknown"
        )

        filename = os.path.basename(source)

        page = document.metadata.get(
            "page",
            None
        )

        page_label = document.metadata.get(
            "page_label",
            None
        )

        file_type = document.metadata.get(
            "file_type",
            "unknown"
        )

        # ---------------------------------------------
        # Split one document at a time
        # ---------------------------------------------

        page_chunks = splitter.split_documents(
            [document]
        )

        for chunk_index, chunk in enumerate(
            page_chunks
        ):

            # -----------------------------------------
            # PDF / paginated document
            # -----------------------------------------

            if page is not None:

                chunk_id = (
                    f"{filename}"
                    f"_page_{page}"
                    f"_chunk_{chunk_index}"
                )

            # -----------------------------------------
            # CSV / TXT / DOCX / XLSX / PPTX
            # -----------------------------------------

            else:

                chunk_id = (
                    f"{filename}"
                    f"_doc_{document_index}"
                    f"_chunk_{chunk_index}"
                )

            chunk.metadata = {
                **document.metadata,
                **chunk.metadata,

                "chunk_id": chunk_id,

                "page": page,

                "page_label": page_label,

                "file_type": file_type
            }

            final_chunks.append(chunk)

    return final_chunks