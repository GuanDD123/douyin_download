def filter_name(text: str, illegal_char: set[str], default: str = ""):
    for i in illegal_char:
        text = text.replace(i, " ")
    text = text.strip().strip(".")

    return text or default


def clear_spaces(string: str):
    """将连续的空格转换为单个空格"""
    return " ".join(string.split())
