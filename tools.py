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


def get_identifier_from_url(url):
    """
    Get the identifier out of a DOI or arXiv URL.

    :param url: An input URL.
    :returns: A tuple ``(type, identifier)``. Returns ``(None, None)`` if \
            could not match.
    """
    type = None
    identifier = None

    if "dx.doi.org" in url:
        type = "doi"
        identifier = url[url.find("dx.doi.org") + 11:]
    elif "arxiv.org/abs" in url:
        type = "arxiv_id"
        identifier = url[url.find("arxiv.org/abs/") + 14:]

    return (type, identifier)


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
