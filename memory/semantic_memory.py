import json
from pathlib import Path
import math
from config.settings import DATA_DIR
from models.semantic_document import SemanticDocument
from llm.embedding_client import EmbeddingClient
import sqlite3
import numpy as np

class SemanticMemory:
    """
    Stores semantic documents.

    This memory stores concepts instead of
    entity attributes.

    Embedding search will be added later.
    """

    _embedding_client = EmbeddingClient()

    DATABASE_PATH = (
        Path(DATA_DIR)
        / "semantic.db"
    )

    @classmethod
    def _connect(
        cls
    ):
        """
        Return a SQLite connection.
        """

        cls.DATABASE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        return sqlite3.connect(
            cls.DATABASE_PATH
        )
    
    @classmethod
    def _serialize_embedding(
        cls,
        embedding: list[float]
    ) -> bytes:
        """
        Convert an embedding into
        SQLite BLOB bytes.
        """

        return np.asarray(
            embedding,
            dtype=np.float32
        ).tobytes()


    @classmethod
    def _deserialize_embedding(
        cls,
        blob: bytes
    ) -> list[float]:
        """
        Convert SQLite BLOB back into
        a Python list.
        """

        if not blob:
            return []

        return np.frombuffer(
            blob,
            dtype=np.float32
        ).tolist()
    
    @classmethod
    def initialize_database(
        cls
    ):
        """
        Create semantic database if it
        does not already exist.
        """

        connection = cls._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (

                id TEXT PRIMARY KEY,

                text TEXT NOT NULL,

                embedding BLOB,

                metadata TEXT

            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_documents_text

            ON documents(text)
            """
        )
        connection.commit()

        connection.close()
                
    @classmethod
    def add_document(
        cls,
        document: SemanticDocument
    ):

        #
        # SQLite
        #
        if not document.embedding:

                document.embedding = cls._embedding_client.embed(
                    document.text
                )

        cls.initialize_database()

        connection = cls._connect()

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO documents
                (
                    id,
                    text,
                    embedding,
                    metadata
                )
                VALUES
                (
                    ?, ?, ?, ?
                )
                """,
                (
                    document.id,
                    document.text,
                    cls._serialize_embedding(
                        document.embedding
                    ),
                    json.dumps(
                        document.metadata
                    )
                )
            )

            connection.commit()
            
        finally:

            connection.close()

    @classmethod
    def all_documents(
        cls
    ) -> list[SemanticDocument]:
        """
        Return every stored semantic document.

        SQLite is now the source of truth.
        """

        cls.initialize_database()

        connection = cls._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                text,
                embedding,
                metadata
            FROM documents
            """
        )

        rows = cursor.fetchall()

        connection.close()

        documents = []

        for row in rows:

            documents.append(

                SemanticDocument(

                    id=row[0],

                    text=row[1],

                    embedding=cls._deserialize_embedding(
                        row[2]
                    ),
                    metadata=json.loads(
                        row[3]
                    ) if row[3] else {}

                )

            )

        return documents

    @classmethod
    def clear(cls):

        #
        # SQLite
        #

        cls.initialize_database()

        connection = cls._connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM documents
            """
        )

        connection.commit()

        connection.close()

    @classmethod
    def verify_database(
        cls
    ) -> bool:
        """
        Verify SQLite integrity.
        """

        cls.initialize_database()

        connection = cls._connect()

        try:

            cursor = connection.cursor()

            cursor.execute(
                "PRAGMA integrity_check"
            )

            result = cursor.fetchone()

            return (
                result[0] == "ok"
            )

        finally:

            connection.close()

    @classmethod
    def statistics(
        cls
    ):
        """
        Return semantic memory statistics.
        """

        documents = cls.all_documents()

        return {

            "documents": len(
                documents
            ),

            "database": str(
                cls.DATABASE_PATH
            )

        }

    @classmethod
    def delete_document(
        cls,
        document_id: str
    ):
        """
        Delete one semantic document.
        """

        cls.initialize_database()

        connection = cls._connect()

        try:

            cursor = connection.cursor()

            cursor.execute(
                """
                DELETE FROM documents
                WHERE id = ?
                """,
                (
                    document_id,
                )
            )

            connection.commit()

        finally:

            connection.close()


    @classmethod
    def update_document(
        cls,
        document: SemanticDocument
    ):
        """
        Update an existing document.

        Internally uses add_document().
        """

        cls.add_document(
            document
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