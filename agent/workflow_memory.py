import json

from pathlib import Path

from config.settings import DATA_DIR

from models.execution_event import ExecutionEvent
from agent.behavior_history import BehaviorHistory

class WorkflowMemory:

    MEMORY_FILE = (
        Path(DATA_DIR)
        / "workflow_memory.json"
    )

    @classmethod
    def load_memory(
        cls
    ):

        if not cls.MEMORY_FILE.exists():
            return {
                "workflows": {}
            }

        try:

            with open(
                cls.MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {
                "workflows": {}
            }
        
    @classmethod
    def save_memory(
        cls,
        memory: dict
    ):

        cls.MEMORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory,
                f,
                indent=4
            )

    @classmethod
    def learn_workflows(cls):

        history = BehaviorHistory.get_history()

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
    def record_execution(
        cls,
        event: ExecutionEvent
    ):
        """
        Update workflow knowledge after a completed execution.

        Future:
            - Learn repeated workflows
            - Learn execution patterns
            - Learn successful sequences
        """
        pass

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