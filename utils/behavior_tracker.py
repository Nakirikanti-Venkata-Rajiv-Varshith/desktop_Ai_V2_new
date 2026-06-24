# utils/behavior_tracker.py

import json
from pathlib import Path
from datetime import datetime

from config.settings import DATA_DIR


class BehaviorTracker:

    FILE_PATH = Path(DATA_DIR) / "user_behavior.json"

    @classmethod
    def log(
        cls,
        tool_name: str,
        function_name: str,
        arguments: dict | None = None,
        user_text: str | None = None
    ):

        try:

            cls.FILE_PATH.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            if cls.FILE_PATH.exists():

                try:

                    with open(
                        cls.FILE_PATH,
                        "r",
                        encoding="utf-8"
                    ) as f:

                        data = json.load(f)

                        if not isinstance(
                            data,
                            list
                        ):
                            data = []

                except Exception:

                    data = []

            else:

                data = []

            data.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "user_text": user_text,
                    "tool": tool_name,
                    "function": function_name,
                    "arguments": arguments or {}
                }
            )

            data = data[-1000:]

            with open(
                cls.FILE_PATH,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=4
                )

        except Exception as e:

            print(
                f"BehaviorTracker Error: {e}"
            )