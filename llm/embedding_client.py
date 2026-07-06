from ollama import Client

from config.settings import OLLAMA_EMBEDDING_MODEL


class EmbeddingClient:
    """
    Generates embeddings using a local Ollama embedding model.

    Responsibilities
    ----------------
    - Convert text into an embedding vector.
    - Return only the embedding.

    It NEVER:
    - Stores embeddings.
    - Performs similarity search.
    - Reads or writes memory.
    """

    def __init__(self):

        self.client = Client(
            host="http://localhost:11434"
        )

    def embed(
        self,
        text: str
    ) -> list[float]:
        """
        Generate an embedding for the given text.

        Parameters
        ----------
        text : str
            Text to embed.

        Returns
        -------
        list[float]
            Embedding vector.
        """

        text = text.strip()

        if not text:
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        try:

            response = self.client.embed(
                model=OLLAMA_EMBEDDING_MODEL,
                input=text
            )

            return response["embeddings"][0]

        except Exception as e:

            raise RuntimeError(
                "Failed to generate embedding using Ollama."
            ) from e