from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        length_function=len
    )

    chunks = text_splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):

        source = chunk.metadata["source"]

        page = chunk.metadata["page"]

        chunk.metadata["chunk_id"] = f"{source}_{page}_{i}"

    return chunks