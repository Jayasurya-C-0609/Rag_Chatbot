import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader
)


def load_file(path):

    extension = os.path.splitext(path)[1].lower()

    if extension == ".pdf":
        loader = PyPDFLoader(path)
        file_type = "pdf"

    elif extension == ".txt":
        loader = TextLoader(
            path,
            encoding="utf-8"
        )
        file_type = "txt"

    elif extension == ".csv":
        loader = CSVLoader(path)
        file_type = "csv"

    elif extension in [".xlsx", ".xls"]:
        loader = UnstructuredExcelLoader(path)
        file_type = "excel"

    elif extension == ".docx":
        loader = Docx2txtLoader(path)
        file_type = "docx"

    elif extension == ".pptx":
        loader = UnstructuredPowerPointLoader(path)
        file_type = "pptx"

    else:
        raise ValueError(
            f"Unsupported file format: {extension}"
        )

    documents = loader.load()

    for doc in documents:
        doc.metadata["file_type"] = file_type

    return documents


def load_files(folder):

    documents = []

    for filename in os.listdir(folder):

        if filename.startswith("."):
            continue
        path = os.path.join(
            folder,
            filename
        )

        if not os.path.isfile(path):
            continue

        try:

            docs = load_file(path)

            documents.extend(docs)

            print(
                f"Loaded: {filename} "
                f"({len(docs)} documents)"
            )

        except Exception as e:

            print(
                f"Failed to load {filename}: {e}"
            )

    return documents