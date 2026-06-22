from llm.ollama_client import OllamaClient


class Router:

    def __init__(self):

        self.llm = OllamaClient()

    def route(
        self,
        user_text
    ):

        return self.llm.route(
            user_text
        )