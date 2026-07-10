from datetime import datetime

from pydantic import BaseModel, Field

from models.accounting.bank_transaction import (
    BankTransaction
)


class StatementMetadata(BaseModel):
    """
    Metadata describing one bank statement.
    """

    bank_name: str

    statement_file: str

    statement_period_from: str | None = None

    statement_period_to: str | None = None

    processed_at: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )


class BankStatement(BaseModel):
    """
    One parsed bank statement.

    This is the output of the BankStatementParser.
    """

    metadata: StatementMetadata

    transactions: list[BankTransaction]