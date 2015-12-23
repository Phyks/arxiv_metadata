def replaceAll(text, dic):
    """Replace all the dic keys by the associated item in text"""
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def clean_whitespaces(text):
    """
    Remove double whitespaces and trailing . and , from text.
    """
    return ' '.join(text.strip().rstrip(".,").split())
