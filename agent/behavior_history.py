import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from config.settings import DATA_DIR
from models.execution_event import ExecutionEvent


class BehaviorHistory:

    HISTORY_FILE = (
        Path(DATA_DIR)
        / "behavior_history.json"
    )

    ARCHIVE_DIR = (
        Path(DATA_DIR)
        / "behavior_archive"
    )

    MAX_HISTORY = 5000

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

        history = cls._archive_old_executions(
            history
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

    @classmethod
    def _archive_old_executions(
        cls,
        history: dict
    ) -> dict:
        """
        Archive executions older than MAX_HISTORY.

        Older executions are grouped by month
        (YYYY-MM.json).

        Returns the trimmed history.
        """

        executions = history.get(
            "executions",
            []
        )

        if len(executions) <= cls.MAX_HISTORY:
            return history

        archive_items = executions[
            :-cls.MAX_HISTORY
        ]

        remaining_items = executions[
            -cls.MAX_HISTORY:
        ]

        monthly_archives = defaultdict(
            list
        )

        for execution in archive_items:

            timestamp = execution.get(
                "timestamp"
            )

            if not timestamp:
                continue

            month = timestamp[:7]

            monthly_archives[
                month
            ].append(
                execution
            )

        cls.ARCHIVE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        for month, items in monthly_archives.items():

            archive_file = (
                cls.ARCHIVE_DIR
                / f"{month}.json"
            )

            if archive_file.exists():

                try:

                    with open(
                        archive_file,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        archive = json.load(f)

                except Exception:

                    archive = {
                        "executions": []
                    }

            else:

                archive = {
                    "executions": []
                }

            archive.setdefault(
                "executions",
                []
            )

            archive[
                "executions"
            ].extend(
                items
            )

            with open(
                archive_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    archive,
                    f,
                    indent=4
                )

        history[
            "executions"
        ] = remaining_items

        return history