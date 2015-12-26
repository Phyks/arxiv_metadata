"""
This file contains GET routes methods.
"""
import bottle

import database
import tools


def fetch_papers(db):
    """
    Fetch all matching papers.

    .. code-block:: bash

        GET /papers
        Accept: application/vnd.api+json


    Filtering is possible using ``id=ID``, ``doi=DOI``, ``arxiv_id=ARXIV_ID`` \
    or any combination of these GET parameters. Other parameters are ignored.


    .. code-block:: json

        {
            "data": [
                {
                    "type": "papers",
                    "id": 1,
                    "attributes": {
                        "doi": "10.1126/science.1252319",
                        "arxiv_id": "1401.2910"
                    },
                    "links": {
                        "self": "/papers/1"
                    },
                    "relationships": {
                        "cite": {
                            "links": {
                                "related": "/papers/1/relationships/cite"
                            }
                        },
                        …
                    }
                }
            ]
        }

    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    filters = {k: bottle.request.params[k]
               for k in bottle.request.params
               if k in ["id", "doi", "arxiv_id"]}
    resources = db.query(database.Paper).filter_by(**filters).all()
    if resources:
        return tools.APIResponse(tools.pretty_json({
            "data": [resource.json_api_repr(db) for resource in resources]
        }))
    return bottle.HTTPError(404, "Not found")


def fetch_papers_by_id(id, db):
    """
    Fetch a paper identified by its internal id.

    .. code-block:: bash

        GET /papers/1
        Accept: application/vnd.api+json


    .. code-block:: json

        {
            "data": {
                "type": "papers",
                "id": 1,
                "attributes": {
                    "doi": "10.1126/science.1252319",
                    "arxiv_id": "1401.2910"
                },
                "links": {
                    "self": "/papers/1"
                },
                "relationships": {
                    "cite": {
                        "links": {
                            "related": "/papers/1/relationships/cite"
                        }
                    },
                    …
                }
            }
        }

    :param id: The id of the requested paper.
    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    resource = db.query(database.Paper).filter_by(id=id).first()
    if resource:
        return tools.APIResponse(tools.pretty_json({
            "data": resource.json_api_repr(db)
        }))
    return bottle.HTTPError(404, "Not found")


def fetch_relationship(id, name, db):
    """
    Fetch relationships of the given type associated with the given paper.

    .. code-block:: bash

        GET /papers/1/relationships/cite
        Accept: application/vnd.api+json


    .. code-block:: json

        {
            "links": {
                "self": "/papers/1/relationships/cite",
                "related": "/papers/1/cite"
            },
            "data": [
                {
                    "type": "papers",
                    "id": 2,
                },
                …
            ]
        }

    :param id: The id of the requested paper.
    :param name: The name of the requested relationship for this paper.
    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    reversed = (
        "reverse" in bottle.request.params and
        bottle.request.params["reverse"] != 0
    )
    resource = db.query(database.Paper).filter_by(id=id).first()
    if resource:
        response = {
            "links": {
                "self": "/papers/%d/relationships/%s" % (id, name),
                "related": "/papers/%d/%s" % (id, name),
            },
            "data": [
            ]
        }
        # Tags are handled differently
        if name == "tags":
            for t in resource.tags:
                response["data"].append({
                    "type": name,
                    "id": t.id
                })
        else:
            if reversed:
                relationships = resource.related_by
            else:
                relationships = resource.related_to
            for r in relationships:
                if r.relationship.name == name:
                    response["data"].append({"type": name, "id": r.right_id})
        return tools.APIResponse(tools.pretty_json(response))
    return bottle.HTTPError(404, "Not found")


def fetch_tags(db):
    """
    Fetch all matching tags.

    .. code-block:: bash

        GET /tags
        Accept: application/vnd.api+json


    Filtering is possible using ``id=ID``, ``name=NAME`` or any combination of
    these GET parameters. Other parameters are ignored.


    .. code-block:: json

        {
            "data": [
                {
                    "type": "tags",
                    "id": 1,
                    "attributes": {
                        "name": "foobar",
                    },
                    "links": {
                        "self": "/tags/1"
                    }
                }
            ]
        }

    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    filters = {k: bottle.request.params[k]
               for k in bottle.request.params
               if k in ["id", "name"]}
    resources = db.query(database.Tags).filter_by(**filters).all()
    if resources:
        return tools.APIResponse(tools.pretty_json({
            "data": [resource.json_api_repr() for resource in resources]
        }))
    return bottle.HTTPError(404, "Not found")


def fetch_tags_by_id(id, db):
    """
    Fetch a tag identified by its internal id.

    .. code-block:: bash

        GET /tag/1
        Accept: application/vnd.api+json


    .. code-block:: json

        {
            "data": {
                "type": "papers",
                "id": 1,
                "attributes": {
                    "doi": "10.1126/science.1252319",
                    "arxiv_id": "1401.2910"
                },
                "links": {
                    "self": "/papers/1"
                },
                "relationships": {
                    "cite": {
                        "links": {
                            "related": "/papers/1/relationships/cite"
                        }
                    },
                    …
                }
            }
        }

    :param id: The id of the requested tag.
    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    resource = db.query(database.Tags).filter_by(id=id).first()
    if resource:
        return tools.APIResponse(tools.pretty_json({
            "data": resource.json_api_repr()
        }))
    return bottle.HTTPError(404, "Not found")
