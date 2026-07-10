from pydantic import BaseModel


class ParsedHeader(BaseModel):
    """
    Parsed information extracted from the
    header line of a bank transaction.
    """

    transaction_number: int

    date: str

    header_description: str

    amount: float

    balance: float

    entry_type: str