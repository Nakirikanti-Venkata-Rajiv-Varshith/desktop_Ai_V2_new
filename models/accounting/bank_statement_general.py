from pydantic import BaseModel

from models.accounting.journal_entry import JournalEntry


class StatementPeriod(BaseModel):

    from_date: str

    to_date: str


class StatementMetadata(BaseModel):

    bank_name: str

    statement_file: str

    statement_period: StatementPeriod

    processed_at: str


class BankStatementGeneral(BaseModel):

    metadata: StatementMetadata

    journal_entries: list[JournalEntry]