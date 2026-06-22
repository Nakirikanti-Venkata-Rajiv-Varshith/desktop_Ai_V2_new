from llm.prompts.base_prompt import BASE_PROMPT

from llm.prompts.gmail_prompt import GMAIL_PROMPT
from llm.prompts.youtube_prompt import YOUTUBE_PROMPT
from llm.prompts.system_prompt import SYSTEM_TOOL_PROMPT
from llm.prompts.browser_prompt import BROWSER_PROMPT
from llm.prompts.file_prompt import FILE_PROMPT


class PromptBuilder:

    MAP = {
        "gmail": GMAIL_PROMPT,
        "youtube": YOUTUBE_PROMPT,
        "system": SYSTEM_TOOL_PROMPT,
        "browser": BROWSER_PROMPT,
        "file": FILE_PROMPT
    }

    @classmethod
    def build(
        cls,
        tool_name,
        user_text
    ):

        return (
            BASE_PROMPT
            + "\n\n"
            + cls.MAP[tool_name]
            + "\n\nUser:\n"
            + user_text
        )