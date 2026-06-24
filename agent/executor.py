from tools.registry import TOOLS
from utils.global_events import event_bus


class Executor:


    
    def execute(
        self,
        tool_name,
        function_name,
        arguments
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

        event_bus.emit(
            f"Completed {tool_name}.{function_name}"
        )

        return result