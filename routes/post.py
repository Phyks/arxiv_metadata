"""
This file contains POST routes methods.
"""
import bottle
import json
from sqlalchemy.exc import IntegrityError

import database
import tools
from reference_fetcher import arxiv


def create_paper(db):
    """
    Create a new resource identified by its DOI or arXiv eprint id.

    ```
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
    ```

    ```
    {
        "data": {
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
                    TODO
                }
            }
        }
    }
    ```
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
        "data": paper.json_api_repr()
    }
    # TODO: Return a 202 as the resource has been accepted but is not yet
    # processed, especially since its relationships have not yet been fetched.
    headers = {"Location": "/papers/%d" % (paper.id,)}
    return tools.APIResponse(status=202,
                             body=tools.pretty_json(response),
                             headers=headers)


def create_by_doi(doi, db):
    """
    Create a new resource identified by its DOI, if it does not exist.

    Return None if insertion failed, the Paper object otherwise.
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


def create_by_arxiv(arxiv, db):
    """
    Create a new resource identified by its arXiv eprint ID, if it does not
    exist.

    Return None if insertion failed, the Paper object otherwise.
    """
    paper = database.Paper(arxiv_id=arxiv)

    # Try to fetch an arXiv id
    doi = arxiv.get_doi(arxiv)
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
