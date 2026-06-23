from llm.chat_client import ChatClient

from llm.prompts.chat_prompt import CHAT_PROMPT


class ChatTool:

    def __init__(self):

        self.client = ChatClient()

    def respond(
        self,
        message: str
    ):

        prompt = CHAT_PROMPT.format(
            query=message
        )

        return self.client.chat(
            prompt
        )