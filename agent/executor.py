from tools.registry import TOOLS
from utils.global_events import event_bus
from utils.behavior_tracker import BehaviorTracker

class Executor:


    
    def execute(
        self,
        tool_name,
        function_name,
        arguments,
        user_text=None
    ):
        
        event_bus.emit(
                f"Executing {tool_name}.{function_name}"
            )

        tool_class = TOOLS.get(tool_name)

        if not tool_class:
            raise ValueError(
                f"Unknown tool: {tool_name}"
            )

        tool = tool_class()

        fn = getattr(
            tool,
            function_name
        )

        result = fn(
            **arguments
        )
        
        BehaviorTracker.log(
            tool_name,
            function_name,
            arguments,
            user_text
        )

        event_bus.emit(
            f"Completed {tool_name}.{function_name}"
        )

        return result