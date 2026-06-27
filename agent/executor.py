from tools.registry import TOOLS
from utils.global_events import event_bus
from memory.memory_manager import MemoryManager


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

        memory = MemoryManager()

        fn = getattr(
            tool,
            function_name
        )

        try:

            result = fn(
                **arguments
            )

            memory.log_execution(
                tool=tool_name,
                function=function_name,
                arguments=arguments,
                success=True
            )

            event_bus.emit(
                f"Completed {tool_name}.{function_name}"
            )

            return result

        except Exception:

            memory.log_execution(
                tool=tool_name,
                function=function_name,
                arguments=arguments,
                success=False
            )

            raise