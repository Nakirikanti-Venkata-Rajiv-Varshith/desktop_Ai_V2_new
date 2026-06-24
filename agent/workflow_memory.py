import json
from pathlib import Path

from config.settings import DATA_DIR


class WorkflowMemory:

    HISTORY_FILE = (
        Path(DATA_DIR)
        / "user_behavior.json"
    )

    @classmethod
    def load_history(cls):

        if not cls.HISTORY_FILE.exists():
            return []

        try:

            with open(
                cls.HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return []

    @classmethod
    def learn_workflows(cls):

        history = cls.load_history()

        workflows = {}

        for item in history:

            user_text = item.get(
                "user_text"
            )

            if not user_text:
                continue

            phrase = (
                user_text
                .strip()
                .lower()
            )

            workflows.setdefault(
                phrase,
                {
                    "count": 0,
                    "steps": []
                }
            )

            workflows[phrase][
                "count"
            ] += 1

            step = {
                "tool": item.get(
                    "tool"
                ),
                "function": item.get(
                    "function"
                ),
                "arguments": item.get(
                    "arguments",
                    {}
                )
            }

            if step not in workflows[
                phrase
            ]["steps"]:

                workflows[
                    phrase
                ]["steps"].append(
                    step
                )

        return workflows
    
    @classmethod
    def get_workflow(
        cls,
        user_text: str,
        min_count: int = 5
    ):

        workflows = cls.learn_workflows()

        workflow = workflows.get(
            user_text.lower()
        )

        if not workflow:
            return None

        if workflow["count"] < min_count:
            return None

        return workflow