from pydantic import BaseModel


class BankTransaction(BaseModel):
    """
    Represents a single transaction extracted
    from a bank statement.

    This model preserves the transaction exactly
    as it appears in the bank statement.
    Accounting interpretation is performed later.
    """

    transaction_number: int

    date: str

    description: str

    amount: float

    transaction_type: str
    # "DR" or "CR"

    balance: float

    raw_text: str