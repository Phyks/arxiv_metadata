"""
This file contains various utility functions.
"""


def replaceAll(text, replace_dict):
    """
    Replace all the ``replace_dict`` keys by their associated item in ``text``.
    """
    for i, j in replace_dict.items():
        text = text.replace(i, j)
    return text


def clean_whitespaces(text):
    """
    Remove double whitespaces and trailing "." and "," from text.
    """
    return ' '.join(text.strip().rstrip(".,").split())
