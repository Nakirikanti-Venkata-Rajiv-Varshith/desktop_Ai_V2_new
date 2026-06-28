from conversation.conversation_manager import ConversationManager

manager = ConversationManager()

manager.add_user_message(
    "Open Gmail"
)

manager.add_assistant_message(
    "Opened Gmail"
)

manager.add_user_message(
    "Compose email"
)

print(
    manager.build_recent_context()
)