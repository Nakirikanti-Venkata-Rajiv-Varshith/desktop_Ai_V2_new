from config.settings import OLLAMA_MODEL

from llm.prompts.accounting_prompt import ACCOUNTING_PROMPT

from models.accounting.bank_statement_general import (
    BankStatementGeneral
)

from models.accounting.bank_statement_request import (
    BankStatementRequest
)


class InstructorFinance:
    """
    Finance-specific Instructor wrapper.

    Handles all accounting related structured
    generation using Instructor.

    Prompt engineering for accounting lives
    inside this class.
    """

    def __init__(
        self,
        client
    ):

        self.client = client

    def _build_prompt(
            self,
            request: BankStatementRequest
        ) -> str:
            """
            Build the accounting prompt for the
            supplied bank statement.
            """

            return f"""
        {ACCOUNTING_PROMPT}

        ==================================================
        STATEMENT FILE
        ==================================================

        {request.statement_file}

        ==================================================
        BANK STATEMENT
        ==================================================

        {request.pdf_text}
        """


    def generate_bank_statement_general(
        self,
        request: BankStatementRequest
    ) -> BankStatementGeneral:
        """
        Convert an extracted bank statement into
        structured journal entries.
        """

        prompt = self._build_prompt(
            request
        )

        try:

            response = self.client.chat.completions.create(

                model=OLLAMA_MODEL,

                response_model=BankStatementGeneral,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            print("\n")
            print("=" * 80)
            print("BANK STATEMENT GENERAL")
            print("=" * 80)
            print(response)
            print("=" * 80)
            print("\n")

            return response

        except Exception as e:

            print("\n")
            print("=" * 80)
            print("BANK STATEMENT GENERAL ERROR")
            print("=" * 80)
            print(e)
            print("=" * 80)
            print("\n")

            raise