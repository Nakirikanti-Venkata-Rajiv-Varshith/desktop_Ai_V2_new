import json

from models.tool_plan import ToolPlan
from models.task_plan import TaskPlan


class Parser:

    def parse(
        self,
        raw_text
    ):

        data = json.loads(
            raw_text
        )

        if "steps" not in data:

            data = {
                "steps": [data]
            }

        return TaskPlan(
            **data
        )