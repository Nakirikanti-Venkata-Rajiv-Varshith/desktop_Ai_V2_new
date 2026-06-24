from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    query: str