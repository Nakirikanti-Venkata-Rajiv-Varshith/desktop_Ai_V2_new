from conversation.conversation_manager import ConversationManager
from agent.turn_analyzer import TurnAnalyzer
from memory.memory_manager import MemoryManager
from agent.planner import Planner
from agent.executor import Executor


class Orchestrator:

    def __init__(self):

        self.conversation = ConversationManager()

        self.turn_analyzer = TurnAnalyzer()

        self.memory = MemoryManager()

        self.planner = Planner()

        self.executor = Executor()

    def run(
        self,
        user_text: str
    ):

        context = self.conversation.build_context(
            user_text
        )

  
        analysis = self.turn_analyzer.analyze(
            context
        )

        self.conversation.add_user_message(
            user_text
        )


        analysis = self.memory.process_turn(
            analysis
        )

    

        plan = self.planner.create_plan(
            analysis,
            user_text
        )
      
        results = []

        if not plan.steps:
            return [
                "Hello! How can I help you today?"
            ]

        for step in plan.steps:

            result = self.executor.execute(
                step.tool,
                step.function,
                step.arguments,
                step.user_text
            )

            results.append(
                result
            )

        assistant_message = (
            results[-1]
            if results
            else "Done."
        )

        self.conversation.add_assistant_message(
            str(assistant_message)
        )

        return results