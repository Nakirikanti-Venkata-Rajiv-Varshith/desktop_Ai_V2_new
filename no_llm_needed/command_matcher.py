import json
from pathlib import Path

class CommandMatcher:

    def __init__(self):
        json_path = (
            Path(__file__)
            .parent
            / "predefined_commands.json"
        )

        with open(json_path, "r") as f:
            self.commands = json.load(f)

    def match(self, user_text: str):
        key = user_text.lower().strip()

        return self.commands.get(key)