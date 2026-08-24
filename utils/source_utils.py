import os

def extract_sources(documents):

    sources = []

    for doc in documents:

        source = os.path.basename(
            doc.metadata.get(
                "source",
                "Unknown"
            )
        )

        page = doc.metadata.get("page")

        source_info = {
            "file": source,
            "page": (
                page + 1
                if isinstance(page, int)
                else None
            )
        }

        if source_info not in sources:
            sources.append(source_info)

    return sources
def group_sources(sources):

    grouped = {}

    for source in sources:

        file = source["file"]
        page = source["page"]

        if file not in grouped:
            grouped[file] = []

        if page not in grouped[file]:
            grouped[file].append(page)

    return grouped