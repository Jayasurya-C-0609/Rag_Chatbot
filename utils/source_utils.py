import os


def extract_sources(documents):

    grouped = {}

    for doc in documents:

        source = os.path.basename(
            doc.metadata.get(
                "source",
                "Unknown"
            )
        )

        if not source:
            continue

        page = doc.metadata.get("page")

        # Convert zero-based page to one-based page
        if isinstance(page, int):
            page = page + 1
        else:
            page = None

        if source not in grouped:
            grouped[source] = set()

        # Don't store None pages
        if page is not None:
            grouped[source].add(page)

    return [
        {
            "file": file,
            "pages": sorted(pages)
        }
        for file, pages in grouped.items()
    ]


def group_sources(sources):

    grouped = {}

    for source in sources:

        file = source["file"]
        pages = source.get("pages", [])

        if file not in grouped:
            grouped[file] = []

        for page in pages:

            if page not in grouped[file]:
                grouped[file].append(page)

    return grouped