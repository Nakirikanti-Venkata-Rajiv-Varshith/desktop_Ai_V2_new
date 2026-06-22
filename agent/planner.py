from agent.router import Router
from agent.parser import Parser

from llm.builders.prompt_builder import PromptBuilder
from llm.ollama_client import OllamaClient


class Planner:

    def __init__(self):

        self.router = Router()

        self.parser = Parser()

        self.llm = OllamaClient()

    def create_plan(
        self,
        user_text
    ):

        tool_name = self.router.route(
            user_text
        )

        prompt = (
            PromptBuilder
            .build(
                tool_name,
                user_text
            )
        )

        raw = self.llm.generate(
            prompt
        )

        return self.parser.parse(
            raw
        )