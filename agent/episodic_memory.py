import json
from pathlib import Path
from datetime import date, datetime
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

        print("=" * 80)
        print("EPISODIC MEMORY FILE")
        print(cls.FILE_PATH)
        print("=" * 80)

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
    def _get_episodes(
        cls
    ) -> list[dict]:
        """
        Return all stored episodes.

        This is the single helper used by
        retrieval APIs.
        """

        memory = cls.load_memory()

        return memory.get(
            "episodes",
            []
        )
    
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
    ):

        return {
            "timestamp": event.timestamp.isoformat(),
            "category": event.tool,
            "event": event.experience
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

    @classmethod
    def get_recent_events(
        cls,
        limit: int = 20
    ):
        """
        Return the most recent episodic events.

        Parameters
        ----------
        limit:
            Maximum number of recent events to return.

        Returns
        -------
        list[dict]
            Newest events first.
        """

        memory = cls.load_memory()

        episodes = memory.get(
            "episodes",
            []
        )

        return list(
            reversed(
                episodes[-limit:]
            )
        )
    
    @classmethod
    def get_events_by_category(
        cls,
        category: str
    ):
        """
        Return all episodic events
        belonging to a category.
        """

        memory = cls.load_memory()

        episodes = memory.get(
            "episodes",
            []
        )

        category = category.lower()

        results = []

        for episode in episodes:

            if (
                episode.get(
                    "category",
                    ""
                ).lower()
                ==
                category
            ):
                results.append(
                    episode
                )

        return results
    
    @classmethod
    def get_events_for_date(
        cls,
        target_date: date
    ):
        """
        Return every event that occurred
        on the given date.
        """

        memory = cls.load_memory()

        episodes = memory.get(
            "episodes",
            []
        )

        results = []

        for episode in episodes:

            timestamp = datetime.fromisoformat(
                episode["timestamp"]
            )

            if timestamp.date() == target_date:

                results.append(
                    episode
                )

        return results
    
    @classmethod
    def get_last_event(
        cls
    ):
        """
        Return the latest recorded episode.

        Returns
        -------
        dict | None
        """

        memory = cls.load_memory()

        episodes = memory.get(
            "episodes",
            []
        )

        if not episodes:

            return None

        return episodes[-1]
    
    @classmethod
    def get_events_today(
        cls
    ):
        """
        Return all events recorded today.
        """

        return cls.get_events_for_date(
            date.today()
        )
    
    @classmethod
    def get_events_between(
        cls,
        start: datetime,
        end: datetime
    ):
        """
        Return all events whose timestamps
        fall within the given time range.

        Parameters
        ----------
        start:
            Inclusive start time.

        end:
            Inclusive end time.
        """

        episodes = cls._get_episodes()

        results = []

        for episode in episodes:

            timestamp = datetime.fromisoformat(
                episode["timestamp"]
            )

            if start <= timestamp <= end:

                results.append(
                    episode
                )

        return results
    
    @classmethod
    def get_all_events(cls):
        """
        Return every stored episode.
        """

        return cls._get_episodes()

    @classmethod
    def search_events(
        cls,
        keyword: str
    ):
        """
        Search episodic memory using a keyword.

        The search is case-insensitive and
        checks both the category and event
        fields.
        """

        episodes = cls._get_episodes()

        keyword = keyword.lower()

        results = []

        for episode in episodes:

            category = episode.get(
                "category",
                ""
            ).lower()

            event = episode.get(
                "event",
                ""
            ).lower()

            if (
                keyword in category
                or
                keyword in event
            ):

                results.append(
                    episode
                )

        return results

    @classmethod
    def clear_memory(
        cls
    ):
        """
        Remove all stored episodes.

        Useful during development
        and testing.
        """

        cls.save_memory(
            {
                "episodes": []
            }
        )