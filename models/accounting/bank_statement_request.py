from pydantic import BaseModel


class BankStatementRequest(BaseModel):
    """
    Input required to convert a bank statement
    into journal entries.
    """

    statement_file: str

    pdf_text: str