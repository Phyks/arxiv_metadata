"""
Various utility functions.
"""
import bottle
import json


def pretty_json(data):
    """
    Return pretty-printed JSON-formatted string.

    :param data: A string to be converted.
    :returns: A pretty-printed JSON-formatted string.
    """
    return json.dumps(data,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))


class APIResponse(bottle.HTTPResponse):
    """
    Extend bottle.HTTPResponse base class to add Content-Type header.
    """
    def __init__(self, body='', status=None, headers=None, **more_headers):
        if headers is None:
            headers = {}
        headers["Content-Type"] = "application/vnd.api+json"
        super(APIResponse, self).__init__(body,
                                          status,
                                          headers,
                                          **more_headers)
