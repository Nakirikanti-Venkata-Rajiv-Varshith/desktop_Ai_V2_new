from enum import Enum


class ResponseType(str, Enum):

    CHAT = "chat"

    TOOL = "tool"

    KNOWLEDGE = "knowledge"