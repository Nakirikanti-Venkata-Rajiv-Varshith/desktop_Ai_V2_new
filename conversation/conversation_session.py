from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class ConversationSession(BaseModel):
    """
    Represents a single conversation session.

    A session tracks the lifetime of a conversation
    from the first user message until it is reset.
    """

    session_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    created_at: datetime = Field(
        default_factory=datetime.now
    )

    updated_at: datetime = Field(
        default_factory=datetime.now
    )

    is_active: bool = True