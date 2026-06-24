import re


def split_commands(text: str):
    """
    Split compound commands into executable steps.

    Examples:
    - open youtube and search for songs and play first video
    - open chrome then open github
    - search python tutorials, open first result, summarize it
    """

    text = text.strip()

    separators = [
        r"\s+and\s+then\s+",
        r"\s+then\s+",
        r"\s*,\s*",
        r"\s*;\s*"
    ]

    pattern = "|".join(separators)

    commands = re.split(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    results = []

    for cmd in commands:

        cmd = cmd.strip()

        if not cmd:
            continue

        # Split on "and" ONLY when it looks like
        # multiple actions are chained together.
        action_keywords = [
            "open",
            "search",
            "play",
            "pause",
            "resume",
            "skip",
            "like",
            "comment",
            "subscribe",
            "send",
            "email",
            "compose",
            "summarize",
            "read",
            "show",
            "create",
            "delete",
            "refresh",
            "close",
            "go back",
            "go forward"
        ]

        lower = cmd.lower()

        if " and " in lower:

            parts = re.split(
                r"\s+and\s+",
                cmd,
                flags=re.IGNORECASE
            )

            temp = []

            for part in parts:
                part = part.strip()

                if any(
                    part.lower().startswith(keyword)
                    for keyword in action_keywords
                ):
                    temp.append(part)
                else:
                    if temp:
                        temp[-1] += " and " + part
                    else:
                        temp.append(part)

            results.extend(temp)

        else:
            results.append(cmd)

    return results