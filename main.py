#!/usr/bin/env python3
import bottle
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import database
import routes
import tools

# Initialize db and include the SQLAlchemy plugin in bottle
engine = create_engine('sqlite:///%s' % (config.database,), echo=True)
create_session = sessionmaker(bind=engine)
database.Base.metadata.create_all(engine)

app = bottle.Bottle()
plugin = sqlalchemy.Plugin(
    # SQLAlchemy engine created with create_engine function.
    engine,
    # SQLAlchemy metadata, required only if create=True.
    database.Base.metadata,
    # Keyword used to inject session database in a route (default 'db').
    keyword='db',
    # If it is true, execute `metadata.create_all(engine)` when plugin is
    # applied (default False).
    create=False,
    # If it is true, plugin commit changes after route is executed (default
    # True).
    commit=True,
    # If it is true and keyword is not defined, plugin uses **kwargs argument
    # to inject session database (default False).
    use_kwargs=False,
    # Create session method
    create_session=create_session
)

app.install(plugin)


# Routes
@app.get("/")
def index():
    return tools.APIResponse(tools.pretty_json({
        "papers": "/papers/?id={id}&doi={doi}&arxiv_id={arxiv_id}",
    }))

app.get("/papers", callback=routes.get.fetch_papers)
app.get("/papers/<id:int>", callback=routes.get.fetch_papers_by_id)
app.get("/papers/<id:int>/relationships/<name>",
        callback=routes.get.fetch_relationship)
app.get("/papers/<id:int>/<name>",
        callback=routes.get.fetch_relationship)
app.route("/papers/<id:int>", method="DELETE",
          callback=routes.delete.delete_paper)
app.route("/papers/<id:int>/relationships/<name>", method="DELETE",
          callback=routes.delete.delete_relationship)

app.get("/tags", callback=routes.get.fetch_tags)
app.get("/tags/<id:int>", callback=routes.get.fetch_tags_by_id)
app.route("/tags/<id:int>", method="DELETE",
          callback=routes.delete.delete_tag)


app.post("/papers", callback=routes.post.create_paper)
app.post("/tags", callback=routes.post.create_tag)

app.post("/papers/<id:int>/relationships/<name>",
         callback=routes.post.update_relationships)
# Complete replacement of relationships is forbidden
app.route("/papers/<id:int>/relationships/<name>", method="PATCH",
          callback=lambda id, name: bottle.HTTPError(403, "Forbidden"))


if __name__ == "__main__":
    routes.post.fetch_citations_in_queue(create_session)
    app.run(host=config.host, port=config.port, debug=(not config.production))
