"""
This file contains DELETE routes methods.
"""
import bottle

import database
import json
import tools


def delete_paper(id, db):
    """
    Delete a given paper.

    .. code-block:: bash

        DELETE /papers/1
        Accept: application/vnd.api+json


    .. code-block:: bash

        HTTP 204

    :param id: The id of the requested paper to be deleted.
    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    resource = db.query(database.Paper).filter_by(id=id).first()
    if resource:
        db.delete(resource)
        return tools.APIResponse(status=204, body="")
    return bottle.HTTPError(404, "Not found")


def delete_relationship(id, name, db):
    """
    Delete a given relationship

    .. code-block:: bash

        DELETE /papers/1/relationships/cite
        Content-Type: application/vnd.api+json
        Accept: application/vnd.api+json

        {
            "data": [
                { "type": "cite", "id": "2" },
                …
            ]
        }


    .. code-block:: bash

        HTTP 204

    :param id: The id of the requested paper from which the relationship \
            should be deleted.
    :param name: The name of the relationship to delete from.
    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    data = json.loads(bottle.request.body.read().decode("utf-8"))
    # Validate the request
    if "data" not in data:
        return bottle.HTTPError(403, "Forbidden")
    # Filter data, invalid entries are ignored
    data = [i for i in data["data"]
            if "type" in i and i["type"] == name and "id" in i]
    # Complete replacement (data == []) is forbidden
    if len(data) == 0:
        return bottle.HTTPError(403, "Forbidden")
    # Delete all the requested relationships
    for i in data:
        if i["type"] == "tags":
            # Handle tags separately
            tag = db.query(database.Tag).filter_by(id=i["id"]).first()
            paper = db.query(database.Paper).filter_by(id=id).first()
            if paper is None or tag is None:
                # An error occurred => 403
                return bottle.HTTPError(403, "Forbidden")
            try:
                paper.tags.remove(tag)
            except ValueError:
                # An error occurred => 403
                return bottle.HTTPError(403, "Forbidden")
            db.flush()
        else:
            relationship = (db.query(database.RelationshipAssociation)
                            .filter_by(left_id=id, right_id=i["id"])
                            .filter(database.Relationship.name == name)
                            .first())
            if relationship is None:
                # An error occurred => 403
                return bottle.HTTPError(403, "Forbidden")
            db.delete(relationship)
    # Return an empty 204 on success
    return tools.APIResponse(status=204, body="")
