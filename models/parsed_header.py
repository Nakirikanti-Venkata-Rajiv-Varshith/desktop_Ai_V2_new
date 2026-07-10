from pydantic import BaseModel


class ParsedHeader(BaseModel):

    transaction_number: int

    date: str

    amount: float

    balance: float

    is_credit: bool