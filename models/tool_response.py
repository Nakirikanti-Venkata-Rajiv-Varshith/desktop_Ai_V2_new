from pydantic import BaseModel


class ToolResponse(BaseModel):
    status: str
    message: str