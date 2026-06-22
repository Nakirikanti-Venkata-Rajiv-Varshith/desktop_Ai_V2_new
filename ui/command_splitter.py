def split_commands(text):

    text = text.replace(" and then ", "|")
    text = text.replace(" then ", "|")
    text = text.replace(" and ", "|")

    return [
        cmd.strip()
        for cmd in text.split("|")
        if cmd.strip()
    ]