from pydantic import BaseModel
from datetime import datetime
from pydantic import Field

class ExecutionEvent(BaseModel):

    tool: str

    function: str

    arguments: dict

    success: bool

    experience: str | None = None

    user_text: str | None = None

    timestamp: datetime = Field(
        default_factory=datetime.now
    )