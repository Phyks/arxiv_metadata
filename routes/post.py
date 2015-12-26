"""
This file contains POST routes methods.
"""
import bottle
import json
import threading
from sqlalchemy.exc import IntegrityError

import config
import database
import tools
from reference_fetcher import arxiv


def create_paper(db):
    """
    Create a new paper identified by its DOI or arXiv eprint id.

    .. code-block:: bash

        POST /papers
        Content-Type: application/vnd.api+json
        Accept: application/vnd.api+json

        {
            "data": {
                "doi": "10.1126/science.1252319",
                // OR
                "arxiv_id": "1401.2910"
            }
        }


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

    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    data = json.loads(bottle.request.body.read().decode("utf-8"))
    # Validate the request
    if("data" not in data or
       "type" not in data["data"] or
       data["data"]["type"] != "papers" or
       ("doi" not in data["data"] and "arxiv_id" not in data["data"])):
        return bottle.HTTPError(403, "Forbidden")

    data = data["data"]

    if "doi" in data:
        paper = create_by_doi(data["doi"], db)
    elif "arxiv_id" in data:
        paper = create_by_arxiv(data["arxiv"], db)

    if paper is None:
        return bottle.HTTPError(409, "Conflict")

    # Return the resource
    response = {
        "data": paper.json_api_repr(db)
    }
    # Import "cite" relation
    add_cite_relationship(paper, db)
    # Return 200 with the correct body
    headers = {"Location": "/papers/%d" % (paper.id,)}
    return tools.APIResponse(status=200,
                             body=tools.pretty_json(response),
                             headers=headers)


def create_by_doi(doi, db):
    """
    Create a new resource identified by its DOI, if it does not exist.

    :param doi: The DOI of the paper.
    :param db: A database session.
    :returns: ``None`` if insertion failed, the ``Paper`` object otherwise.
    """
    paper = database.Paper(doi=doi)

    # Try to fetch an arXiv id
    arxiv_id = arxiv.get_arxiv_eprint_from_doi(doi)
    if arxiv_id:
        paper.arxiv_id = arxiv_id

    # Add it to the database
    try:
        db.add(paper)
        db.flush()
    except IntegrityError:
        # Unique constraint violation, paper already exists
        db.rollback()
        return None

    # Return the paper
    return paper


def create_by_arxiv(arxiv_id, db):
    """
    Create a new resource identified by its arXiv eprint ID, if it does not
    exist.

    :param arxiv_id: The arXiv eprint ID.
    :param db: A database session.
    :returns: ``None`` if insertion failed, the ``Paper`` object otherwise.
    """
    paper = database.Paper(arxiv_id=arxiv_id)

    # Try to fetch an arXiv id
    doi = arxiv.get_doi(arxiv_id)
    if doi:
        paper.doi = doi

    # Add it to the database
    try:
        db.add(paper)
        db.flush()
    except IntegrityError:
        # Unique constraint violation, paper already exists
        db.rollback()
        return None

    # Return the paper
    return paper


def add_cite_relationship(paper, db):
    """
    Add the "cite" relationships between the provided paper and the papers
    referenced by it.

    :param paper: The paper to fetch references from.
    :param db: A database session
    :returns: Nothing.
    """
    # If paper is on arXiv
    if paper.arxiv_id is not None:
        # Get the cited DOIs
        cited_urls = arxiv.get_cited_dois(paper.arxiv_id)
        # Filter out the ones that were not matched
        cited_urls = [cited_urls[k]
                      for k in cited_urls if cited_urls[k] is not None]
        for url in cited_urls:
            type, identifier = tools.get_identifier_from_url(url)
            if type is None:
                # No identifier found
                continue
            # Get the associated paper in the db
            right_paper = (db.query(database.Paper)
                           .filter(getattr(database.Paper, type) == identifier)
                           .first())
            if right_paper is None:
                # If paper is not in db, add it
                if type == "doi":
                    right_paper = create_by_doi(identifier, db)
                elif type == "arxiv_id":
                    right_paper = create_by_arxiv(identifier, db)
                else:
                    continue
                # Push this paper on the queue for update of cite relationships
                queue = database.CitationProcessingQueue()
                queue.paper = right_paper
                try:
                    db.add(queue)
                except IntegrityError:
                    # Unique constraint violation, relationship already exists
                    db.rollback()
            # Update the relationships
            update_relationship_backend(paper.id, right_paper.id, "cite", db)
    # If paper is not on arXiv, nothing to do
    else:
        return


def fetch_citations_in_queue(create_session):
    """
    Process the first item in the queue, waiting for citation processing.

    i.. note::

            Calls itself recursively after the time defined in ``config``, so
            that queued articles are processed concurrently.

    :param create_session: a ``SQLAlchemy`` ``sessionmaker``.
    :returns: Nothing.
    """
    # Get a db Session
    db = create_session()
    queued = db.query(database.CitationProcessingQueue).first()
    if queued:
        print("Processing citation relationships for %s." % (queued.paper,))
        # Process this paper
        add_cite_relationship(queued.paper, db)
        # Remove this paper from queue
        db.delete(queued)
        # Commit to the database
        try:
            db.commit()
        except:
            db.rollback()
    # Call this function again after a while
    threading.Timer(
        config.queue_polling_interval,
        lambda: fetch_citations_in_queue(create_session)
    ).start()


def update_relationships(id, name, db):
    """
    Update the relationships associated to a given paper.

    .. code-block:: bash

        POST /papers/1/relationships/cite
        Content-Type: application/vnd.api+json
        Accept: application/vnd.api+json

        {
            "data": [
                { "type": "cite", "id": "2" },
                …
            ]
        }


    .. code-block:: json

        HTTP 204

    :param id: The id of the paper to update relationships.
    :param name: The name of the relationship to update.
    :param db: A database session, passed by Bottle plugin.
    :returns: No content. 204 on success, 403 on error.
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
    # Update all the relationships
    for i in data:
        if i["type"] == "tags":
            # Handle tags separately
            tag = db.query(database.Tag).filter_by(id=i["id"]).first()
            paper = db.query(database.Paper).filter_by(id=id).first()
            if paper is None or tag is None:
                # An error occurred => 403
                return bottle.HTTPError(403, "Forbidden")
            paper.tags.append(tag)
            db.add(paper)
            db.flush()
        else:
            updated = update_relationship_backend(id, i["id"], name, db)
            if updated is None:
                # An error occurred => 403
                return bottle.HTTPError(403, "Forbidden")
    # Return an empty 204 on success
    return tools.APIResponse(status=204, body="")


def update_relationship_backend(left_id, right_id, name, db):
    """
    Backend method to update a single relationship between two papers.

    :param left_id: ID of the paper on the left of the relationship.
    :param right_id: ID of the paper on the right of the relationship.
    :param name: Name of the relationship between the two papers.
    :param db: A database session.
    :returns: The updated left paper on success, ``None`` otherwise.
    """
    # Load necessary resources
    left_paper = db.query(database.Paper).filter_by(id=left_id).first()
    right_paper = db.query(database.Paper).filter_by(id=right_id).first()
    if left_paper is None or right_paper is None:
        # Abort
        return None
    relationship = db.query(database.Relationship).filter_by(name=name).first()
    if relationship is None:
        relationship = database.Relationship(name=name)
        db.add(relationship)
        db.flush()
    # Update the relationship
    a = database.RelationshipAssociation(relationship_id=relationship.id)
    a.right_paper = right_paper
    left_paper.related_to.append(a)
    try:
        db.add(a)
        db.add(left_paper)
    except IntegrityError:
        # Unique constraint violation, relationship already exists
        db.rollback()
        return None
    return left_paper


def create_tag(db):
    """
    Create a new tag.

    .. code-block:: bash

        POST /tags
        Content-Type: application/vnd.api+json
        Accept: application/vnd.api+json

        {
            "data": {
                "name": "foobar",
            }
        }


    .. code-block:: json

        {
            "data": {
                "type": "tags",
                "id": 1,
                "attributes": {
                    "name": "foobar",
                },
                "links": {
                    "self": "/tags/1"
                }
            }
        }

    :param db: A database session, injected by the ``Bottle`` plugin.
    :returns: An ``HTTPResponse``.
    """
    data = json.loads(bottle.request.body.read().decode("utf-8"))
    # Validate the request
    if("data" not in data or
       "type" not in data["data"] or
       data["data"]["type"] != "tags" or
       "name" not in data["data"]):
        return bottle.HTTPError(403, "Forbidden")

    data = data["data"]

    tag = database.Tag(name=data["name"])

    # Add it to the database
    try:
        db.add(tag)
        db.flush()
    except IntegrityError:
        # Unique constraint violation, paper already exists
        db.rollback()
        return bottle.HTTPError(409, "Conflict")

    # Return the resource
    response = {
        "data": tag.json_api_repr()
    }
    # Return 200 with the correct body
    headers = {"Location": "/tags/%d" % (tag.id,)}
    return tools.APIResponse(status=200,
                             body=tools.pretty_json(response),
                             headers=headers)
