from pydantic import BaseModel, Field


class ToolPlan(BaseModel):

    tool: str

    function: str

    arguments: dict = Field(
        default_factory=dict
    )

    user_text: str | None = None