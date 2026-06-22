# agent/router.py
from llm.ollama_client import OllamaClient

class Router:
    def __init__(self):
        self.llm = OllamaClient()

    def route(self, user_text: str) -> str:
        return self.llm.route(user_text)