# agent/adaptive_memory.py

import json
from pathlib import Path
from collections import Counter
from config.settings import DATA_DIR


class AdaptiveMemory:

    FILE_PATH = Path(DATA_DIR) / "user_behavior.json"
    PREFERENCES_FILE = Path(DATA_DIR) / "preferences.json"

    @classmethod
    def load_history(cls):

        if not cls.FILE_PATH.exists():
            return []

        try:

            with open(
                cls.FILE_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return []

    @classmethod
    def get_tool_usage(cls):

        history = cls.load_history()

        counter = Counter()

        for item in history:

            tool = item.get(
                "tool"
            )

            if tool:

                counter[tool] += 1

        return dict(counter)

    @classmethod
    def get_most_used_tool(cls):

        usage = cls.get_tool_usage()

        if not usage:
            return None

        return max(
            usage,
            key=usage.get
        )

    @classmethod
    def get_function_usage(
        cls,
        tool_name: str
    ):

        history = cls.load_history()

        counter = Counter()

        for item in history:

            if (
                item.get("tool")
                == tool_name
            ):

                function = item.get(
                    "function"
                )

                counter[
                    function
                ] += 1

        return dict(counter)

    @classmethod
    def get_preference_summary(cls):

        history = cls.load_history()

        if not history:

            return {
                "total_actions": 0,
                "most_used_tool": None,
                "tool_usage": {}
            }

        return {
            "total_actions": len(history),
            "most_used_tool": cls.get_most_used_tool(),
            "tool_usage": cls.get_tool_usage()
        }
        



    @classmethod
    def extract_preferences(cls):

        history = cls.load_history()

        music_platforms = []

        music_queries = []

        for item in history:

            tool = item.get("tool")

            function = item.get("function")

            arguments = item.get(
                "arguments",
                {}
            )

            if tool == "youtube":

                music_platforms.append(
                    "youtube"
                )

            if function in [
                "search_query",
                "search"
            ]:

                query = arguments.get(
                    "query"
                )

                if query:

                    music_queries.append(
                        query
                    )

        platform = None
        confidence = 0.0

        if music_platforms:

            counts = Counter(
                music_platforms
            )

            platform = counts.most_common(
                1
            )[0][0]

            confidence = round(
                counts[platform]
                /
                len(music_platforms),
                2
            )

        return {

            "music_platform":
                platform,

            "confidence":
                confidence,

            "favorite_queries": list(
                dict.fromkeys(
                    music_queries
                )
            )[-10:]
        }
    
    @classmethod
    def save_preferences(cls):

        preferences = cls.extract_preferences()

        cls.PREFERENCES_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.PREFERENCES_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                preferences,
                f,
                indent=4
            )

        return preferences
    
    @classmethod
    def load_preferences(cls):

        if not cls.PREFERENCES_FILE.exists():

            return {}

        try:

            with open(
                cls.PREFERENCES_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {}