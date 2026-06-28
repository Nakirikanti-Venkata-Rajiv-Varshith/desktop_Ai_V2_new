# agent/planner.py
from agent.router import Router
from agent.parser import Parser
from memory.memory_manager import MemoryManager
from models.turn_analysis import TurnAnalysis
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
        self.llm = InstructorClient()
        self.matcher = CommandMatcher() 
        self.memory = MemoryManager()


    def create_plan(
        self,
        analysis: TurnAnalysis,
        user_text: str
    ) -> TaskPlan:
        """
        Coordinates intent tracking by checking the rapid rule match engine 
        before routing text downstream to the local Ollama LLM setup.
        """
        # user_text = self._apply_semantic_memory(
        #     user_text
        # )

        user_text = self.memory.prepare_user_text(
            user_text
        )
        print("=" * 60)
        print("PLANNER CREATE_PLAN CALLED")
        print(f"user_text = {user_text}")
        print("=" * 60)
            
        workflow_plan = self.memory.get_workflow_plan(
            user_text
        )

        if workflow_plan:

            event_bus.emit(
                f"Workflow hit: {user_text}"
            )

            return workflow_plan
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
            return self._build_task_plan(tool_plan)



        # event_bus.emit(
        #     "Running Turn Analyzer"
        # )

        # analysis = self.turn_analyzer.analyze(
        #     user_text
        # )

        # analysis = self.memory.process_turn(
        #     analysis
        # )
        return self._build_plan_from_analysis(
            analysis,
            user_text
        )

    def _build_task_plan(
        self,
        steps: ToolPlan | list[ToolPlan]
    ) -> TaskPlan:
        """
        Build a TaskPlan from one or more ToolPlans.
        """

        if isinstance(
            steps,
            ToolPlan
        ):
            steps = [steps]

        return TaskPlan(
            steps=steps
        )
    
    def _build_plan_from_analysis(
        self,
        analysis,
        user_text: str
    ) -> TaskPlan:

        if analysis.response_type == ResponseType.CHAT:
            return self._build_chat_plan(
                user_text
            )

        elif analysis.response_type == ResponseType.KNOWLEDGE:
            return self._build_chat_plan(
                user_text
            )

        elif analysis.response_type == ResponseType.TOOL:

            if (
                analysis.tool_call is None
                or analysis.tool_call.tool is None
                or analysis.tool_call.function is None
            ):
                return self._empty_plan()

            event_bus.emit(
                f"Generated plan: {analysis.tool_call.tool}.{analysis.tool_call.function}"
            )

            tool_plan = self._build_tool_plan(
                analysis,
                user_text
            )

            return self._build_task_plan(
                tool_plan
            )

        return self._empty_plan()
    
    def _build_chat_plan(
        self,
        user_text: str
    ) -> TaskPlan:

        tool_plan = ToolPlan(
            tool="chat",
            function="respond",
            arguments={
                "message": user_text
            },
            user_text=user_text
        )

        return self._build_task_plan(
            tool_plan
        )
    
    def _build_tool_plan(
        self,
        analysis,
        user_text: str
    ) -> ToolPlan:

        return ToolPlan(
            tool=analysis.tool_call.tool,
            function=analysis.tool_call.function,
            arguments=analysis.tool_call.arguments,
            user_text=user_text
        )

    def _empty_plan(
        self
    ) -> TaskPlan:

        return TaskPlan(
            steps=[]
        )