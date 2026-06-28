from llm.instructor_client import InstructorClient

from llm.prompts.turn_analyzer_prompt import (
    build_turn_analyzer_prompt
)

from conversation.conversation_context import (
    ConversationContext
)

from models.turn_analysis import TurnAnalysis


class TurnAnalyzer:

    def __init__(self):

        self.client = InstructorClient()

    def analyze(
        self,
        context: ConversationContext
    ) -> TurnAnalysis:
        """
        Analyze the current user request using
        the conversation context.
        """
        print("=" * 80)
        print("RECENT CONTEXT")
        print("=" * 80)
        print(context.recent_context)
        print()

        prompt = build_turn_analyzer_prompt(
            recent_context=context.recent_context,
            user_message=context.current_message
        )

        return self.client.generate_turn_analysis(
            prompt
        )