import re


class KeywordReranker:

    def __init__(self):

        self.stop_words = {
            "what",
            "are",
            "the",
            "is",
            "a",
            "an",
            "of",
            "for",
            "in",
            "to",
            "and",
            "on",
            "with",
            "how",
            "can",
            "does",
            "do"
        }


    def tokenize(self, text):

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

        return [
            word
            for word in words
            if word not in self.stop_words
        ]


    def score(self, query, document):

        query_words = set(
            self.tokenize(query)
        )

        document_words = set(
            self.tokenize(
                document.page_content
            )
        )

        if not query_words:
            return 0.0

        matched = (
            query_words &
            document_words
        )

        return (
            len(matched)
            /
            len(query_words)
        )


    def rerank(
        self,
        query,
        documents,
        top_k=6
    ):

        if not documents:
            return []

        ranked = []

        for doc in documents:

            score = self.score(
                query,
                doc
            )

            ranked.append(
                (doc, score)
            )


        ranked.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]