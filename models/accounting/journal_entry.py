from pydantic import BaseModel

from models.accounting.journal_line import JournalLine


class SourceTransaction(BaseModel):

    description: str

    amount: float


class JournalEntry(BaseModel):

    voucher_number: int

    voucher_type: str = "Journal"

    date: str

    entries: list[JournalLine]

    narration: str

    source_transaction: SourceTransaction