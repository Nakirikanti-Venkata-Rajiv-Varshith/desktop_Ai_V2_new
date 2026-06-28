from pydantic import BaseModel, Field

from conversation.conversation_turn import ConversationTurn


class ConversationHistory(BaseModel):
    """
    Stores the conversation history
    for the current session.
    """

    turns: list[ConversationTurn] = Field(
        default_factory=list
    )