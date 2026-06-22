from tools.registry import TOOLS


class Executor:

    def execute(
        self,
        tool_name,
        function_name,
        arguments
    ):

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

        return fn(**arguments)