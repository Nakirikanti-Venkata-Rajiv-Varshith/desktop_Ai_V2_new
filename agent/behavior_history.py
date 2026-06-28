import json
from datetime import datetime
from pathlib import Path

from config.settings import DATA_DIR
from models.execution_event import ExecutionEvent


class BehaviorHistory:

    HISTORY_FILE = (
        Path(DATA_DIR)
        / "behavior_history.json"
    )

    @classmethod
    def load_history(cls):

        if not cls.HISTORY_FILE.exists():
            return {
                "executions": []
            }

        try:

            with open(
                cls.HISTORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {
                "executions": []
            }

    @classmethod
    def save_history(
        cls,
        history: dict
    ):

        cls.HISTORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                history,
                f,
                indent=4
            )

    @classmethod
    def record_execution(
        cls,
        event: ExecutionEvent
    ):
        """
        Record a completed execution.

        BehaviorHistory is the source of truth for
        execution history.
        """

        history = cls.load_history()

        history.setdefault(
            "executions",
            []
        )

        history["executions"].append(
            {
                "timestamp": datetime.now().isoformat(),
                "tool": event.tool,
                "function": event.function,
                "arguments": event.arguments,
                "success": event.success,
                "user_text": event.user_text
            }
        )

        cls.save_history(
            history
        )

    @classmethod
    def get_history(cls):

        return (
            cls.load_history()
            .get(
                "executions",
                []
            )
        )

    @classmethod
    def clear_history(cls):

        cls.save_history(
            {
                "executions": []
            }
        )