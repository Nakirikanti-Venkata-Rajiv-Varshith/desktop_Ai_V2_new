from llm.instructor_client import InstructorClient

from llm.prompts.turn_analyzer_prompt import (
    build_turn_analyzer_prompt
)

from models.turn_analysis import TurnAnalysis


class TurnAnalyzer:

    def __init__(self):

        self.client = InstructorClient()

    def analyze(
        self,
        user_message: str,
        recent_context: str = ""
    ) -> TurnAnalysis:

        prompt = build_turn_analyzer_prompt(
            recent_context=recent_context,
            user_message=user_message
        )

        return self.client.generate_turn_analysis(
            prompt
        )