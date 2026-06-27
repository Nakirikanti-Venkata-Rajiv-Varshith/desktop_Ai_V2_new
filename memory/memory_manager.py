from agent.workflow_memory import WorkflowMemory
from agent.adaptive_memory import AdaptiveMemory
from agent.entity_memory import EntityMemory
from models.turn_analysis import TurnAnalysis
from utils.global_events import event_bus
from tools.registered_tools_metadata import REGISTERED_TOOL_METADATA

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
        # for argument_name, memory_attribute in memory_bindings.items():

        #     if memory_attribute is None:
        #         continue

        #     if argument_name not in analysis.tool_call.arguments:
        #         continue

        #     print(
        #         f"{argument_name} = "
        #         f"{analysis.tool_call.arguments[argument_name]}"
        #     )

        # return analysis

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
        pass

    def get_workflow(
        self,
        user_text: str
    ):
        """
        Retrieve a previously learned workflow.
        """
        return WorkflowMemory.get_workflow(
            user_text
        )

    def get_preferences(self) -> dict:
        """
        Retrieve stored user preferences.
        """
        return AdaptiveMemory.load_preferences()