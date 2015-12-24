"""
This file contains GET routes methods.
"""
import bottle

import database
import tools


def fetch_papers(db):
    """
    Fetch all matching papers.

    ```
    GET /papers
    Accept: application/vnd.api+json
    ```

    Filtering is possible using `id=ID`, `doi=DOI`, `arxiv_id=ARXIV_ID` or any
    combination of these GET parameters. Other parameters are ignored.

    ```
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
                    TODO
                }
            }
        ]
    }
    ```
    """
    filters = {k: bottle.request.params[k]
               for k in bottle.request.params
               if k in ["id", "doi", "arxiv_id"]}
    resources = db.query(database.Paper).filter_by(**filters).all()
    if resources:
        return tools.APIResponse(tools.pretty_json({
            "data": [resource.json_api_repr() for resource in resources]
        }))
    return bottle.HTTPError(404, "Not found")


def fetch_by_id(id, db):
    """
    Fetch a resource identified by its internal id.

    ```
    GET /id/<id>
    Accept: application/vnd.api+json
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
    resource = db.query(database.Paper).filter_by(id=id).first()
    if resource:
        return tools.APIResponse(tools.pretty_json({
            "data": resource.json_api_repr()
        }))
    return bottle.HTTPError(404, "Not found")
