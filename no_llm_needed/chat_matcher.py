CHAT_KEYWORDS = [

    "hello",
    "hi",
    "hey",

    "how are you",
    "how are you doing",
    "how are you feeling",

    "good morning",
    "good afternoon",
    "good evening",

    "thanks",
    "thank you",

    "nice to meet you"
]


def is_chat(text: str) -> bool:

    text = text.lower().strip()

    return any(
        keyword in text
        for keyword in CHAT_KEYWORDS
    )