from pydantic import BaseModel


class JournalLine(BaseModel):

    account: str

    type: str

    amount: float