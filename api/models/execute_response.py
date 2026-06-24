from pydantic import BaseModel


class ExecuteResponse(BaseModel):
    result: list