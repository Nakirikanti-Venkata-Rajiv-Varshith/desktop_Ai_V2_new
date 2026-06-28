from pydantic import BaseModel
from datetime import datetime
from pydantic import Field

class ExecutionEvent(BaseModel):

    tool: str

    function: str

    arguments: dict

    success: bool

    user_text: str | None = None

    timestamp: datetime = Field(
        default_factory=datetime.now
    )