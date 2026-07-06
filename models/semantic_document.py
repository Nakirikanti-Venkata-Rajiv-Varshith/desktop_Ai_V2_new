from uuid import uuid4
from typing import Any

from pydantic import BaseModel, Field


class SemanticDocument(BaseModel):
    """
    Represents a semantic memory document.

    Each document stores a reusable concept,
    its embedding vector, and metadata used
    for semantic retrieval.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the semantic document."
    )

    text: str = Field(
        description="Semantic content to be embedded and searched."
    )

    embedding: list[float] = Field(
        default_factory=list,
        description="Embedding vector generated from the document text."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional information describing the semantic document."
    )