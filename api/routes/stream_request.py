from pydantic import BaseModel


class StreamRequest(BaseModel):
    query: str