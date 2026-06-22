import json

from tools.logger import agent_logger
from models.task_plan import TaskPlan


class Parser:

    @staticmethod
    def parse_and_validate(raw_text: str) -> TaskPlan:

        cleaned = raw_text.strip()
        print("\nPARSER RECEIVED:\n")
        print(cleaned)
        print("\nEND PARSER INPUT\n")

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:

            parsed_json = json.loads(cleaned)

            if "steps" not in parsed_json:
                parsed_json = {
                    "steps": [parsed_json]
                }

            print(type(parsed_json))
            print(parsed_json)
            return TaskPlan(**parsed_json)

        except Exception as e:

            agent_logger.error(
                f"Parser Error: {str(e)}"
            )

            raise