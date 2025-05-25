def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def clean_text(text: str) -> str:
    return text.strip().replace('\n', ' ').replace('\r', ' ')
