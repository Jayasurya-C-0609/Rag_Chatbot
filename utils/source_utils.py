import os

EXCERPT_MAX_CHARS = 200


def extract_sources(documents):
    """
    Extract source metadata from retrieved documents.

    Each source entry contains:
    - ``file``    : bare filename (e.g. "report.pdf")
    - ``page``    : 1-indexed page number
    - ``excerpt`` : first ``EXCERPT_MAX_CHARS`` chars of the chunk text
    """
    sources = []

    for doc in documents:

        source = os.path.basename(
            doc.metadata.get("source", "Unknown")
        )

        page = doc.metadata.get("page")

        if page is not None:
            page = page + 1

        # Build a clean excerpt: collapse whitespace and trim
        raw_text = doc.page_content or ""
        excerpt = " ".join(raw_text.split())[:EXCERPT_MAX_CHARS]
        if len(" ".join(raw_text.split())) > EXCERPT_MAX_CHARS:
            excerpt += "…"

        source_info = {
            "file": source,
            "page": page,
            "excerpt": excerpt,
        }

        # Deduplicate by (file, page) — keep first occurrence
        key = (source, page)
        if not any(
            (s["file"], s["page"]) == key
            for s in sources
        ):
            sources.append(source_info)

    return sources


def group_sources(sources):
    """
    Group sources by filename.

    Returns
    -------
    dict
        ``{filename: [{"page": int, "excerpt": str}, ...]}``
    """
    grouped = {}

    for source in sources:
        file = source["file"]
        page = source["page"]
        excerpt = source.get("excerpt", "")

        if file not in grouped:
            grouped[file] = []

        # Avoid duplicate pages within the same file
        if not any(
            entry["page"] == page
            for entry in grouped[file]
        ):
            grouped[file].append(
                {"page": page, "excerpt": excerpt}
            )

    return grouped