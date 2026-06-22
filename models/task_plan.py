from pydantic import BaseModel
from models.tool_plan import ToolPlan
from llm.ollama_client import OllamaClient
from llm.parser import PlanParser, TaskPlan, ToolPlan
from tools.logger import agent_logger
from no_llm_needed.command_matcher import CommandMatcher


class TaskPlanner:
    """Pipeline component converting natural expressions into structured validation schemas."""

    def __init__(self):

        self.client = OllamaClient()

        self.parser = PlanParser()

        self.command_matcher = CommandMatcher()

    def create_plan(self, user_command: str):

        agent_logger.info(
            f"Planning requested context: '{user_command}'"
        )

        predefined = self.command_matcher.match(
            user_command
        )

        if predefined:

            agent_logger.info(
                "Fast-path command matched."
            )

            return TaskPlan(
                steps=[
                    ToolPlan(
                        **predefined
                    )
                ]
            )

        raw_output = self.client.generate(
            user_command
        )

        validated_schema = (
            self.parser.parse_and_validate(
                raw_output
            )
        )

        return validated_schema

class TaskPlan(BaseModel):
    steps: list[ToolPlan]