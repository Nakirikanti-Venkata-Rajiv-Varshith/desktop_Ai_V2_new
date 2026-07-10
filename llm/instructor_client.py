from openai import OpenAI
import instructor
from instructor import Mode

from config.settings import OLLAMA_MODEL
from models.tool_request import ToolRequest
from models.turn_analysis import TurnAnalysis

from llm.instructor_finance import InstructorFinance
from models.accounting.bank_statement_request import (
    BankStatementRequest
)

class InstructorClient:

    def __init__(self):

        self.client = instructor.from_openai(
            OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            ),
            mode=Mode.JSON
        )

        self.finance = InstructorFinance(
            self.client
        )

    def _generate(
        self,
        *,
        prompt: str,
        response_model,
        title: str
    ):
        """
        Shared Instructor generation helper.

        Handles:
        - Instructor call
        - Logging
        - Error reporting
        """

        try:

            response = self.client.chat.completions.create(

                model=OLLAMA_MODEL,

                response_model=response_model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            print("\n")
            print("=" * 80)
            print(title)
            print("=" * 80)
            print(response)
            print("=" * 80)
            print("\n")

            return response

        except Exception as e:

            print("\n")
            print("=" * 80)
            print(f"{title} ERROR")
            print("=" * 80)
            print(e)
            print("=" * 80)
            print("\n")

            raise

    def generate_tool_request(
        self,
        prompt: str
    ) -> ToolRequest:

        return self._generate(
            prompt=prompt,
            response_model=ToolRequest,
            title="INSTRUCTOR RESPONSE"
        )

    def generate_turn_analysis(
        self,
        prompt: str
    ) -> TurnAnalysis:

        return self._generate(
            prompt=prompt,
            response_model=TurnAnalysis,
            title="TURN ANALYSIS"
        )

    def generate_bank_statement_general(
        self,
        request: BankStatementRequest
    ):

        return self.finance.generate_bank_statement_general(
            request
        )