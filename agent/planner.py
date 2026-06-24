# agent/planner.py
from agent.router import Router
from agent.parser import Parser
from agent.workflow_memory import WorkflowMemory
from agent.adaptive_memory import AdaptiveMemory
from llm.builders.prompt_builder import PromptBuilder
# from llm.ollama_client import OllamaClient

# Core Bridging Imports for Fast-Path and Validation Execution
from no_llm_needed.command_matcher import CommandMatcher
# from models.tool_request import ToolRequest
from models.task_plan import TaskPlan
from models.tool_plan import ToolPlan
from llm.instructor_client import InstructorClient
from no_llm_needed.chat_matcher import is_chat
from utils.global_events import event_bus

class Planner:

    def __init__(self):
        self.router = Router()
        self.parser = Parser()
        # self.llm = OllamaClient()
        self.llm = InstructorClient()
        self.matcher = CommandMatcher()  # Instantiate the fast-path keyword dictionary mapper

    def _apply_preferences(
        self,
        user_text: str
    ) -> str:

        prefs = AdaptiveMemory.load_preferences()

        music_platform = prefs.get(
            "music_platform"
        )

        lowered = user_text.lower()

        music_keywords = [
            "play",
            "song",
            "music",
            "listen"
        ]

        if (
            music_platform == "youtube"
            and any(
                keyword in lowered
                for keyword in music_keywords
            )
            and "youtube" not in lowered
        ):

            user_text += " on youtube"

            event_bus.emit(
                "AdaptiveMemory: Added preferred platform youtube"
            )

        return user_text


    def create_plan(self, user_text: str) -> TaskPlan:
        """
        Coordinates intent tracking by checking the rapid rule match engine 
        before routing text downstream to the local Ollama LLM setup.
        """
        user_text = self._apply_preferences(
            user_text
        )

        workflow = WorkflowMemory.get_workflow(
            user_text
        )

        if workflow:

            event_bus.emit(
                f"Workflow hit: {user_text}"
            )

            steps = []

            for step in workflow["steps"]:

                steps.append(
                    ToolPlan(
                        tool=step["tool"],
                        function=step["function"],
                        arguments=step.get(
                            "arguments",
                            {}
                        ),
                        user_text=user_text
                    )
                )

            return TaskPlan(
                steps=steps
            )
        
        # 1. Evaluate the deterministic No-LLM fast-path registry
        matched_action = self.matcher.match(user_text)
        if matched_action:
            # Safely structure the raw data mapping directly into expected Pydantic records
            tool_plan = ToolPlan(
                tool=matched_action.get("tool"),
                function=matched_action.get("function"),
                arguments=matched_action.get("arguments", {}),
                user_text=user_text
            )
            return TaskPlan(steps=[tool_plan])


        if is_chat(user_text):

                    return TaskPlan(
                        steps=[
                            ToolPlan(
                                tool="chat",
                                function="respond",
                                arguments={
                                    "message": user_text
                                },
                                user_text=user_text
                            )
                        ]
                    )


        event_bus.emit(
            f"Routing query: {user_text}"
        )

        # 3. LLM Processing Fallback Pipeline
        tool_name = self.router.route(user_text)

        event_bus.emit(
            f"Selected tool: {tool_name}"
        )
        if tool_name == "chat":

            return TaskPlan(
                steps=[]
            )

        event_bus.emit(
            "Building prompt"
        )

        prompt = PromptBuilder.build(
            tool_name,
            user_text
        )

        event_bus.emit(
            "Calling Instructor"
        )

        tool_request = self.llm.generate_tool_request(
            prompt
        )

        event_bus.emit(
            f"Generated plan: {tool_request.tool}.{tool_request.function}"
        )

        tool_plan = ToolPlan(
            tool=tool_request.tool,
            function=tool_request.function,
            arguments=tool_request.arguments,
            user_text=user_text
        )

        print(tool_plan)
        return TaskPlan(
            steps=[tool_plan]
        )