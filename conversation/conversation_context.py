from conversation.conversation_session import ConversationSession
from conversation.conversation_turn import ConversationTurn

from pydantic import BaseModel, Field


class ConversationContext(BaseModel):
    """
    Carries the current conversation state
    through the AI pipeline.

    This is the single object passed to
    downstream components such as the
    TurnAnalyzer.
    """

    current_message: str

    session: ConversationSession

    last_turn: ConversationTurn | None = None

    recent_turns: list[ConversationTurn] = Field(
        default_factory=list
    )

    recent_context: str = ""