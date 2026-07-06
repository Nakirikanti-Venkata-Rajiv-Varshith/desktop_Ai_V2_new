from pydantic import BaseModel, Field
from typing import Any


class SemanticCandidate(BaseModel):
    """
    Represents a reusable piece of knowledge that
    should be stored in SemanticMemory.

    A SemanticCandidate is extracted from successful
    executions before it is converted into a
    SemanticDocument.
    """

    text: str = Field(
        description="Human-readable semantic content to embed."
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata describing the semantic object."
    )