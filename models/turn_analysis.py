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


class PreferenceUpdate(BaseModel):

    category: str

    value: str

    confidence: float = 1.0

class Clarification(BaseModel):

    needed: bool = False

    question: str | None = None

class ConversationState(BaseModel):

    topic: str | None = None

    follow_up: bool = False

    references_previous_turn: bool = False

class SafetyAssessment(BaseModel):

    safe: bool = True

    reason: str | None = None

class WorkflowHint(BaseModel):

    reusable: bool = False

    workflow_name: str | None = None

class Context(BaseModel):

    resolved_entities: list[str] = Field(default_factory=list)

    resolved_references: list[str] = Field(default_factory=list)

class TurnAnalysis(BaseModel):
    """
    Complete understanding of a single user message.
    """

    response_type: ResponseType = ResponseType.TOOL

    confidence: float = 1.0

    tool_call: ToolCall | None = None

    facts: list[Fact] = Field(
        default_factory=list)

    preference_updates: list[PreferenceUpdate] = Field(default_factory=list)

    clarification: Clarification = Field(default_factory=Clarification)

    conversation_state: ConversationState = Field(default_factory=ConversationState)

    safety: SafetyAssessment = Field(default_factory=SafetyAssessment)

    workflow_hint: WorkflowHint = Field(default_factory=WorkflowHint)

    context: Context = Field(default_factory=Context)
    
    confidence: float = 1.0
