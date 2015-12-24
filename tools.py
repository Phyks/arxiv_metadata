"""
Various utility functions.
"""
import json


def pretty_json(data):
    """
    Return pretty printed JSON-formatted string.
    """
    return json.dumps(data,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))
