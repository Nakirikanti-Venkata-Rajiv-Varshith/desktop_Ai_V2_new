from agent.planner import Planner
from agent.executor import Executor


class Orchestrator:

    def __init__(self):

        self.planner = Planner()

        self.executor = Executor()

    def run(
        self,
        user_text
    ):

        plan = self.planner.create_plan(
            user_text
        )

        results = []

        if not plan.steps:
            return ["Hello! How can I help you today?"]
        
        for step in plan.steps:

            result = self.executor.execute(
                step.tool,
                step.function,
                step.arguments
            )

            results.append(result)

        return results