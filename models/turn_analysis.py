from pydantic import BaseModel, Field
from typing import Any
from models.response_type import ResponseType

class Fact(BaseModel):
    """
    A durable piece of knowledge extracted from the user's message.
    """

    entity: str = Field(
        description="Entity name in lowercase snake_case."
    )

    attribute: str = Field(
        description="Attribute name in lowercase snake_case."
    )

    value: str = Field(
        description="Literal value for the attribute."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1."
    )


class ToolCall(BaseModel):
    """
    Tool invocation requested by the user.
    """

    tool: str | None = None

    function: str | None = None

    arguments: dict[str, Any] = Field(
        default_factory=dict
    )


class TurnAnalysis(BaseModel):
    """
    Complete understanding of a single user message.
    """

    response_type: ResponseType = ResponseType.TOOL

    confidence: float = 1.0

    requires_clarification: bool = False

    clarification_question: str | None = None

    tool_call: ToolCall | None = None

    facts: list[Fact] = Field(
        default_factory=list
    )