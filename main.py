#!/usr/bin/env python3
from bottle import get, post, run
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base


@get("/doi/<doi:path>")
def doi(doi):
    """
    GET /doi/<DOI>

    {}
    """
    # TODO
    pass


@post("/doi/<doi:path>")
def doi_post(doi):
    """
    POST /doi/<DOI>

    {}
    """
    # TODO
    pass


if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True)
