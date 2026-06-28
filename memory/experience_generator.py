from models.execution_event import ExecutionEvent


class ExperienceGenerator:
    """
    Generates a human-readable experience
    from an ExecutionEvent.

    This class contains no memory logic.

    Its only responsibility is converting an
    execution into a natural language experience.
    """

    @classmethod
    def generate(
        cls,
        event: ExecutionEvent
    ) -> str:

        tool = event.tool
        function = event.function
        arguments = event.arguments or {}

        #
        # Phase 9 (temporary generic implementation)
        #
        # Later we will replace this with
        # richer descriptions.
        #

        if arguments:

            formatted_arguments = ", ".join(
                f"{key}={value}"
                for key, value in arguments.items()
            )

            return (
                f"{tool}.{function}"
                f" ({formatted_arguments})"
            )

        return (
            f"{tool}.{function}"
        )