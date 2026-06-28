from agent.workflow_memory import WorkflowMemory
from agent.preference_memory import PreferenceMemory
from agent.entity_memory import EntityMemory
from agent.behavior_history import BehaviorHistory
from models.execution_event import ExecutionEvent
from models.turn_analysis import TurnAnalysis
from utils.global_events import event_bus
from tools.registered_tools_metadata import REGISTERED_TOOL_METADATA
from models.task_plan import TaskPlan
from models.tool_plan import ToolPlan
from models.execution_event import ExecutionEvent
from agent.episodic_memory import EpisodicMemory
"""
Central gateway for all memory interactions.

Responsibilities:

- Workflow retrieval
- Entity resolution
- Execution logging

Planner and Executor should never access
individual memory modules directly.
"""

class MemoryManager:
    """
    Central gateway for all memory operations.

    Responsibilities
    ----------------
    - Route memory reads.
    - Route memory writes.
    - Hide the implementation details of individual memories.

    It NEVER:
    - Calls the LLM.
    - Performs reasoning.
    - Parses user text.
    - Learns information itself.

    MemoryManager only routes already-understood information.
    """

    def update_from_turn(
        self,
        analysis: TurnAnalysis
    ) -> None:
        """
        Receive a fully analyzed user turn.

        Future routing:

        TurnAnalysis.facts
            -> EntityMemory

        TurnAnalysis.preference_updates
            -> PreferenceMemory

        TurnAnalysis.workflow_hint
            -> WorkflowMemory

        TurnAnalysis.semantic_updates
            -> SemanticMemory
        """
        event_bus.emit(
            "MemoryManager received TurnAnalysis"
        )
        for fact in analysis.facts:

            EntityMemory.remember_entity(
                entity=fact.entity,
                attribute=fact.attribute,
                value=fact.value
            )

    def _get_function_metadata(
        self,
        tool_name: str,
        function_name: str
    ):
        """
        Return the metadata for a specific tool function.
        """

        for tool in REGISTERED_TOOL_METADATA:

            if tool["name"] != tool_name:
                continue

            return tool["functions"].get(
                function_name
            )

        return None

    def _resolve_memory_binding(
        self,
        entity: str,
        attribute: str
    ):
        """
        Resolve a value from memory.

        Currently this delegates to EntityMemory.

        Future:
            - PreferenceMemory
            - WorkflowMemory
            - SemanticMemory
        """

        return EntityMemory.recall_entity(
            entity=entity,
            attribute=attribute
        )

    def enrich_analysis(
        self,
        analysis: TurnAnalysis
    ) -> TurnAnalysis:
        
        print("MM STEP 1")

        if analysis.tool_call is None:
            return analysis

        print("MM STEP 2")
        metadata = self._get_function_metadata(
            analysis.tool_call.tool,
            analysis.tool_call.function
        )

        print(metadata)

        if metadata is None:
            return analysis

        memory_bindings = metadata.get(
            "memory_resolution",
            {}
        )

        print("MM STEP 3")
        print(memory_bindings)

        for argument_name, memory_attribute in memory_bindings.items():

            if memory_attribute is None:
                continue

            if argument_name not in analysis.tool_call.arguments:
                continue

            entity = analysis.tool_call.arguments[
                argument_name
            ]

            resolved = self._resolve_memory_binding(
                entity,
                memory_attribute
            )

            print(
                f"Resolved = {resolved}"
            )

            if resolved is not None:
                    analysis.tool_call.arguments[
                        argument_name
                    ] = resolved

                    print(
                        f"MemoryManager replaced "
                        f"{entity} -> {resolved}"
                    )
        return analysis

    def _update_workflow_memory(
        self,
        event: ExecutionEvent
    ):
        """
        Route workflow learning.
        """

        WorkflowMemory.record_execution(
            event
        )

    def _update_preference_memory(
        self,
        event: ExecutionEvent
    ):
        """
        Route preference learning.
        """

        PreferenceMemory.record_execution(
            event
        )

    def _update_episodic_memory(
        self,
        event: ExecutionEvent
    ):
        """
        Route episodic learning.

        EpisodicMemory stores chronological
        experiences rather than execution details.
        """

        EpisodicMemory.record_execution(
            event
        )

    def log_execution(
        self,
        tool: str,
        function: str,
        arguments: dict,
        success: bool
    ) -> None:
        """
        Receive the result of a completed execution.

        Future routing:

        Execution
            -> BehaviorHistory

        BehaviorHistory
            -> WorkflowMemory

        BehaviorHistory
            -> PreferenceMemory
        """
        event = ExecutionEvent(
            tool=tool,
            function=function,
            arguments=arguments,
            success=success
        )

        self._update_workflow_memory(
            event
        )

        event_bus.emit(
            "MemoryManager received execution"
        )

        # Future:
        # Trigger workflow learning.
        
        BehaviorHistory.record_execution(
            event
        )

        self._update_workflow_memory(
            event
        )

        self._update_preference_memory(
            event
        )

        self._update_episodic_memory(
            event
        )

    def get_workflow(
        self,
        user_text: str
    ):
        """
        Route workflow retrieval.

        Planner should never know which memory
        stores workflows.
        """

        event_bus.emit(
            "MemoryManager checking workflow memory"
        )

        workflow = WorkflowMemory.get_workflow(
            user_text
        )

        return workflow
        
    def prepare_user_text(
        self,
        user_text: str
    ) -> str:
        """
        Prepare user text before planning.

        Future responsibilities:
        - Apply user preferences.
        - Resolve aliases.
        - Resolve semantic shortcuts.
        - Normalize commands.
        """

        prefs = self.get_preferences()

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
                "PreferenceMemory: Added preferred platform youtube"
            )

        return user_text
    

    def get_workflow_plan(
        self,
        user_text: str
    ) -> TaskPlan | None:
        """
        Retrieve a learned workflow and convert it into
        an executable TaskPlan.

        Planner should never know how workflows are stored.
        """

        workflow = self.get_workflow(
            user_text
        )

        if workflow is None:
            return None

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
    
    def process_turn(
        self,
        analysis
    ):
        """
        Process a completed TurnAnalysis.

        Responsibilities:
        - Persist durable facts
        - Enrich tool arguments
        - Future:
            - Preference extraction
            - Semantic enrichment
            - Conversation updates
        """

        self.update_from_turn(
            analysis
        )

        return self.enrich_analysis(
            analysis
        )
    
    def get_preferences(
        self
    ):
        """
        Retrieve learned user preferences.

        Planner and other components should never
        access PreferenceMemory directly.
        """

        return PreferenceMemory.get_preferences()
    

    def apply_preferences(
        self,
        tool_plan
    ):
        """
        Apply learned user preferences
        to a ToolPlan.

        Currently this is a passthrough.
        Future versions may modify:
        - browser
        - quality
        - application
        - defaults
        """

        return tool_plan