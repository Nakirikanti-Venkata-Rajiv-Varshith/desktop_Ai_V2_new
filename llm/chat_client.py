from openai import OpenAI

from config.settings import OLLAMA_MODEL


class ChatClient:

    def __init__(self):

        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )

    def chat(self, prompt: str):

        response = self.client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content