from sentence_transformers import CrossEncoder


class CrossEncoderReranker:

    def __init__(
        self,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"
    ):

        self.model = CrossEncoder(
            model_name
        )


    def rerank(
        self,
        query,
        documents,
        top_k=6,
        score_threshold=0.0
    ):

        if not documents:
            return []


        # -------------------------------------------
        # Create query-document pairs
        # -------------------------------------------

        pairs = [
            (
                query,
                doc.page_content
            )
            for doc in documents
        ]


        # -------------------------------------------
        # Cross Encoder scores
        # -------------------------------------------

        scores = self.model.predict(
            pairs
        )


        ranked = sorted(
            zip(
                documents,
                scores
            ),
            key=lambda x: float(x[1]),
            reverse=True
        )
        print("\n===== RERANK SCORES =====")

        for i, (doc, score) in enumerate(ranked[:15]):

            print(
                i + 1,
                round(float(score), 4),
                doc.metadata.get("source"),
                doc.metadata.get("page")
            )

        print("=========================\n")


        # -------------------------------------------
        # Remove low scoring documents
        # -------------------------------------------

        ranked = [
            (
                doc,
                float(score)
            )
            for doc, score in ranked

            if float(score) >= score_threshold
        ]


        # -------------------------------------------
        # Select documents
        # Preserve page diversity
        # -------------------------------------------

        selected = []

        seen_pages = set()


        for doc, score in ranked:

            source = doc.metadata.get(
                "source",
                ""
            )

            page = doc.metadata.get(
                "page"
            )


            # Page must be unique per file
            page_key = (
                source,
                page
            )


            if page is None:

                selected.append(
                    (
                        doc,
                        score
                    )
                )

            elif page_key not in seen_pages:

                selected.append(
                    (
                        doc,
                        score
                    )
                )

                seen_pages.add(
                    page_key
                )


            if len(selected) >= top_k:
                break


        # -------------------------------------------
        # Fill remaining slots if necessary
        # -------------------------------------------

        if len(selected) < top_k:

            selected_ids = {
                id(doc)
                for doc, _ in selected
            }


            for doc, score in ranked:

                if id(doc) in selected_ids:
                    continue


                selected.append(
                    (
                        doc,
                        score
                    )
                )

                if len(selected) >= top_k:
                    break


        return selected


def remove_duplicate_documents(
    ranked_results):

    seen = set()

    filtered = []


    for doc, score in ranked_results:

        content = (
            doc.page_content
            .strip()
        )


        if content in seen:
            continue


        seen.add(content)

        filtered.append(
            (
                doc,
                score
            )
        )

    return filtered