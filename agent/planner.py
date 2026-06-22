# agent/planner.py
from agent.router import Router
from agent.parser import Parser

from llm.builders.prompt_builder import PromptBuilder
from llm.ollama_client import OllamaClient

# Core Bridging Imports for Fast-Path and Validation Execution
from no_llm_needed.command_matcher import CommandMatcher
from models.task_plan import TaskPlan
from models.tool_plan import ToolPlan


class Planner:

    def __init__(self):
        self.router = Router()
        self.parser = Parser()
        self.llm = OllamaClient()
        self.matcher = CommandMatcher()  # Instantiate the fast-path keyword dictionary mapper

    def create_plan(self, user_text: str) -> TaskPlan:
        """
        Coordinates intent tracking by checking the rapid rule match engine 
        before routing text downstream to the local Ollama LLM setup.
        """
        # 1. Evaluate the deterministic No-LLM fast-path registry
        matched_action = self.matcher.match(user_text)
        if matched_action:
            # Safely structure the raw data mapping directly into expected Pydantic records
            tool_plan = ToolPlan(
                tool=matched_action.get("tool"),
                function=matched_action.get("function"),
                arguments=matched_action.get("arguments", {})
            )
            return TaskPlan(steps=[tool_plan])

        # 2. Add immediate conversational safeguard to prevent Ollama connection timeouts
        clean_text = user_text.lower().strip()
        if clean_text in ["hello", "hi", "hey", "test"]:
            return TaskPlan(steps=[
                ToolPlan(tool="system", function="current_time", arguments={})
            ])

        # 3. LLM Processing Fallback Pipeline
        tool_name = self.router.route(user_text)

        prompt = PromptBuilder.build(tool_name, user_text)

        raw = self.llm.generate(prompt)

        # RECTIFIED: Correctly reference the instance variable 'self.parser' instead of 'Parser'
        return self.parser.parse_and_validate(raw)