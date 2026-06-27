from collections import Counter

from agent.workflow_memory import WorkflowMemory


class IntentMemory:

    MUSIC_WORDS = [
        "play",
        "song",
        "songs",
        "music",
        "listen"
    ]

    @classmethod
    def detect_intent(
        cls,
        text: str
    ):

        text = text.lower()

        if any(
            word in text
            for word in cls.MUSIC_WORDS
        ):
            return "play_music"

        return None
    
    @classmethod
    def extract_entity(
        cls,
        text: str
    ):

        text = text.lower()

        for word in cls.MUSIC_WORDS:

            text = text.replace(
                word,
                ""
            )

        text = (
            text
            .replace("to", "")
            .replace("some", "")
            .strip()
        )

        return text