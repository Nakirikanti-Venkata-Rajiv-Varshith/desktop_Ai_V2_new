from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    """
    Represents one conversation exchange.

    A turn is either a user message or
    an assistant response.
    """

    turn_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    role: str

    message: str

    timestamp: datetime = Field(
        default_factory=datetime.now
    )