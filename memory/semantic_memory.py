import json
from pathlib import Path
import math
from config.settings import DATA_DIR
from models.semantic_document import SemanticDocument
from llm.embedding_client import EmbeddingClient

class SemanticMemory:
    """
    Stores semantic documents.

    This memory stores concepts instead of
    entity attributes.

    Embedding search will be added later.
    """

    _embedding_client = EmbeddingClient()
    MEMORY_FILE = (
        Path(DATA_DIR)
        / "semantic_memory.json"
    )

    @classmethod
    def load_memory(cls):

        if not cls.MEMORY_FILE.exists():
            return {
                "documents": []
            }

        try:

            with open(
                cls.MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {
                "documents": []
            }

    @classmethod
    def save_memory(
        cls,
        memory: dict
    ):

        cls.MEMORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory,
                f,
                indent=4
            )

    @classmethod
    def add_document(
        cls,
        document: SemanticDocument
    ):

        memory = cls.load_memory()

        memory.setdefault(
            "documents",
            []
        )

        if not document.embedding:

            document.embedding = cls._embedding_client.embed(
                document.text
            )

        memory["documents"].append(
            document.model_dump()
        )

        cls.save_memory(
            memory
        )

    @classmethod
    def all_documents(cls):

        memory = cls.load_memory()

        return [
            SemanticDocument(**document)
            for document in memory.get(
                "documents",
                []
            )
        ]

    @classmethod
    def clear(cls):

        cls.save_memory(
            {
                "documents": []
            }
        )

    @classmethod
    def _cosine_similarity(
        cls,
        vector_a: list[float],
        vector_b: list[float]
    ) -> float:

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b
            )
        )

        magnitude_a = math.sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (
            magnitude_a * magnitude_b
        )
   
    @classmethod
    def semantic_search(
        cls,
        query: str
    ) -> SemanticDocument | None:
        """
        Return the semantic document that is
        most similar to the given query.
        """

        # Generate an embedding for the user's query
        query_embedding = cls._embedding_client.embed(
            query
        )

        # Load all stored semantic documents
        documents = cls.all_documents()

        # No documents stored
        if not documents:
            return None

        # Track the best matching document
        best_document = None
        best_score = -1.0

        # Compare the query against every document
        for document in documents:

            score = cls._cosine_similarity(
                query_embedding,
                document.embedding
            )

            if score > best_score:

                best_score = score
                best_document = document

        return best_document