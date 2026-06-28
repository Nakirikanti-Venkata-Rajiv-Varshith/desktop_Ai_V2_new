from conversation.conversation_history import ConversationHistory
from conversation.conversation_session import ConversationSession
from datetime import datetime
from conversation.conversation_turn import ConversationTurn
from conversation.conversation_context import ConversationContext

class ConversationManager:
    """
    Coordinates the current conversation.

    Owns the active session and
    its conversation history.

    Business logic will gradually
    be added in later steps.
    """

    def __init__(self):

        self.session = ConversationSession()

        self.history = ConversationHistory()

    def add_user_message(
        self,
        message: str
    ) -> ConversationTurn:
        """
        Add a user message to the
        current conversation.
        """

        turn = ConversationTurn(
            role="user",
            message=message
        )

        self.history.turns.append(
            turn
        )

        self.session.updated_at = (
            datetime.now()
        )

        return turn
    
    def add_assistant_message(
        self,
        message: str
    ) -> ConversationTurn:
        """
        Add an assistant response to the
        current conversation.
        """

        turn = ConversationTurn(
            role="assistant",
            message=message
        )

        self.history.turns.append(
            turn
        )

        self.session.updated_at = (
            datetime.now()
        )

        return turn
    
    def get_last_turn(
        self
    ) -> ConversationTurn | None:
        """
        Return the most recent conversation turn.
        """

        if not self.history.turns:

            return None

        return self.history.turns[-1]
    
    def get_recent_turns(
        self,
        limit: int = 10
    ) -> list[ConversationTurn]:
        """
        Return the most recent conversation turns.

        Newest turns appear last to preserve
        the natural conversation order.
        """

        if limit <= 0:

            return []

        return self.history.turns[-limit:]
    
    def clear_history(
        self
    ) -> None:
        """
        Remove all conversation turns while
        keeping the current session active.
        """

        self.history.turns.clear()

        self.session.updated_at = (
            datetime.now()
        )

    def reset_session(
        self
    ) -> ConversationSession:
        """
        End the current session and start
        a completely new conversation.
        """

        self.session.is_active = False

        self.session = ConversationSession()

        self.history = ConversationHistory()

        return self.session
    
    def build_context(
        self,
        current_message: str
    ) -> ConversationContext:
        """
        Build a snapshot of the current
        conversation.

        This method never modifies the
        conversation history.
        """

        return ConversationContext(
            current_message=current_message,
            session=self.session,
            last_turn=self.get_last_turn(),
            recent_turns=self.get_recent_turns(),
            recent_context=self.build_recent_context()
        )
    
    def build_recent_context(
        self,
        limit: int = 10
    ) -> str:
        """
        Build a readable conversation summary
        for downstream LLM prompts.
        """

        turns = self.get_recent_turns(
            limit
        )

        if not turns:
            return ""

        lines = []

        for turn in turns:

            lines.append(
                f"{turn.role.title()}: {turn.message}"
            )

        return "\n".join(lines)