import json
from pathlib import Path

from config.settings import DATA_DIR
from models.execution_event import ExecutionEvent


class EpisodicMemory:
    """
    Stores chronological user experiences.

    Unlike BehaviorHistory, this memory stores
    what happened from the user's perspective,
    not how the assistant executed it.
    """

    FILE_PATH = (
        Path(DATA_DIR)
        / "episodic_memory.json"
    )

    @classmethod
    def load_memory(cls):

        if not cls.FILE_PATH.exists():
            return {
                "episodes": []
            }

        try:

            with open(
                cls.FILE_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {
                "episodes": []
            }

    @classmethod
    def save_memory(
        cls,
        memory: dict
    ):

        cls.FILE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.FILE_PATH,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory,
                f,
                indent=4
            )

    @classmethod
    def _build_episode(
        cls,
        event: ExecutionEvent
    ) -> dict:
        """
        Convert an execution into a
        human-readable episode.
        """

        description = (
            f"{event.tool}.{event.function}"
        )

        if (
            event.tool == "youtube"
            and event.function == "search_query"
        ):
            query = event.arguments.get(
                "query",
                ""
            )

            description = (
                f'Searched YouTube for "{query}"'
            )

        elif (
            event.tool == "youtube"
            and event.function == "play_first"
        ):
            description = (
                "Played the first YouTube video"
            )

        elif (
            event.tool == "youtube"
            and event.function == "skip_ad"
        ):
            description = (
                "Skipped a YouTube advertisement"
            )

        elif (
            event.tool == "gmail"
            and event.function == "compose_email"
        ):
            recipient = event.arguments.get(
                "recipient",
                "unknown recipient"
            )

            description = (
                f"Composed an email to {recipient}"
            )

        elif (
            event.tool == "browser"
            and event.function == "open_url"
        ):
            url = event.arguments.get(
                "url",
                ""
            )

            description = (
                f"Opened {url}"
            )

        return {
            "timestamp": event.timestamp.isoformat(),
            "event": description
        }

    @classmethod
    def record_execution(
        cls,
        event: ExecutionEvent
    ):
        """
        Record a chronological experience.
        """

        memory = cls.load_memory()

        memory.setdefault(
            "episodes",
            []
        )

        episode = cls._build_episode(
            event
        )

        memory["episodes"].append(
            episode
        )

        cls.save_memory(
            memory
        )