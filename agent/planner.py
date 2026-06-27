# agent/planner.py
from agent.router import Router
from agent.parser import Parser
from llm.builders.prompt_builder import PromptBuilder
from agent.turn_analyzer import TurnAnalyzer
from memory.memory_manager import MemoryManager
# from llm.ollama_client import OllamaClient

# Core Bridging Imports for Fast-Path and Validation Execution
from models.response_type import ResponseType
from no_llm_needed.command_matcher import CommandMatcher
# from models.tool_request import ToolRequest
from models.task_plan import TaskPlan
from models.tool_plan import ToolPlan
from llm.instructor_client import InstructorClient
from utils.global_events import event_bus

class Planner:

    def __init__(self):
        self.router = Router()
        self.parser = Parser()
        # self.llm = OllamaClient()
        self.llm = InstructorClient()
        self.matcher = CommandMatcher()  # Instantiate the fast-path keyword dictionary mapper
        self.turn_analyzer = TurnAnalyzer()
        self.memory = MemoryManager()

    def _apply_preferences(
        self,
        user_text: str
    ) -> str:

        prefs = self.memory.get_preferences()

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

    # def _apply_semantic_memory(
    #     self,
    #     user_text: str
    # ) -> str:

    #     words = user_text.split()

    #     if len(words) < 2:
    #         return user_text

    #     attribute = (
    #         AttributeResolver
    #         .infer_attribute(
    #             user_text
    #         )
    #     )

    #     if not attribute:
    #         return user_text

    #     entity = words[1]

    #     value = (
    #         EntityResolver
    #         .resolve(
    #             entity,
    #             attribute
    #         )
    #     )

    #     if value:

    #         print(
    #             f"Resolved {entity} -> {value}"
    #         )

    #         user_text = user_text.replace(
    #             entity,
    #             value
    #         )

    #         event_bus.emit(
    #             f"EntityMemory: Resolved {entity} -> {value}"
    #         )

    #     return user_text

    def create_plan(self, user_text: str) -> TaskPlan:
        """
        Coordinates intent tracking by checking the rapid rule match engine 
        before routing text downstream to the local Ollama LLM setup.
        """
        # user_text = self._apply_semantic_memory(
        #     user_text
        # )

        print(user_text)
        print("=" * 60)
        print("PLANNER CREATE_PLAN CALLED")
        print(f"user_text = {user_text}")
        print("=" * 60)
        
        # workflow = self.memory.get_workflow(
        #     user_text
        # )
        workflow = None
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
        print("BEFORE COMMAND MATCHER")
        matched_action = self.matcher.match(user_text)
        print("MATCHED ACTION:", matched_action)
        if matched_action:
            # Safely structure the raw data mapping directly into expected Pydantic records
            tool_plan = ToolPlan(
                tool=matched_action.get("tool"),
                function=matched_action.get("function"),
                arguments=matched_action.get("arguments", {}),
                user_text=user_text
            )
            return TaskPlan(steps=[tool_plan])



        event_bus.emit(
            "Running Turn Analyzer"
        )

        analysis = self.turn_analyzer.analyze(
            user_text
        )

        self.memory.update_from_turn(
            analysis
        )

        analysis = self.memory.enrich_analysis(
            analysis
        )
        
        print("\nTURN ANALYSIS")
        print(analysis)
        print()

        if analysis.response_type == ResponseType.CHAT:

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
        elif analysis.response_type == ResponseType.KNOWLEDGE:

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
        elif analysis.response_type == ResponseType.TOOL:

            if (
                analysis.tool_call is None
                or analysis.tool_call.tool is None
                or analysis.tool_call.function is None
            ):
                return TaskPlan(steps=[])
            
            event_bus.emit(
                f"Generated plan: {analysis.tool_call.tool}.{analysis.tool_call.function}"
            )

            tool_plan = ToolPlan(
                tool=analysis.tool_call.tool,
                function=analysis.tool_call.function,
                arguments=analysis.tool_call.arguments,
                user_text=user_text
            )

            print(tool_plan)
            return TaskPlan(
                steps=[tool_plan]
            )
        
        return TaskPlan(
        steps=[]
    )