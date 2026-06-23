from openai import OpenAI
import instructor
from instructor import Mode

from config.settings import OLLAMA_MODEL
from models.tool_request import ToolRequest


class InstructorClient:

    def __init__(self):

        self.client = instructor.from_openai(
            OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            ),
            mode=Mode.JSON
        )

    def generate_tool_request(
        self,
        prompt: str
    ) -> ToolRequest:

        try:

            response = self.client.chat.completions.create(
                model=OLLAMA_MODEL,

                response_model=ToolRequest,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            print("\n")
            print("=" * 80)
            print("INSTRUCTOR RESPONSE")
            print("=" * 80)
            print(response)
            print("=" * 80)
            print("\n")

            return response

        except Exception as e:

            print("\n")
            print("=" * 80)
            print("INSTRUCTOR ERROR")
            print("=" * 80)
            print(e)
            print("=" * 80)
            print("\n")

            raise