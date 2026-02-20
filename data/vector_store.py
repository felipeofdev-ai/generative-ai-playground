class VectorStore:
    def upsert(self, doc_id: str, embedding: list[float]) -> None:
        _ = (doc_id, embedding)
