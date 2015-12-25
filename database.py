"""
This file contains the database schema in SQLAlchemy format.
"""
from sqlalchemy import event
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship as sqlalchemy_relationship

Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Auto enable foreign keys for SQLite.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# TODO: Backref
class Association(Base):
    # Relationships are to be read "left RELATION right"
    __tablename__ = "association"
    id = Column(Integer, primary_key=True)
    left_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    right_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    relationship_id = Column(Integer,
                             ForeignKey("relationships.id",
                                        ondelete="CASCADE"))
    right_paper = sqlalchemy_relationship("Paper",
                                          foreign_keys=right_id,
                                          back_populates="related_by")
    relationship = sqlalchemy_relationship("Relationship")

    left_paper = sqlalchemy_relationship("Paper",
                                         foreign_keys=left_id,
                                         back_populates="related_to")


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True)
    doi = Column(String(), nullable=True, unique=True)
    arxiv_id = Column(String(25), nullable=True, unique=True)
    # related_to are papers related to this paper (this_paper R …)
    related_to = sqlalchemy_relationship("Association",
                                         foreign_keys="Association.left_id",
                                         back_populates="left_paper")
    # related_by are papers referenced by this paper (… R this_paper)
    related_by = sqlalchemy_relationship("Association",
                                         foreign_keys="Association.right_id",
                                         back_populates="right_paper")

    def __repr__(self):
        return "<Paper(id='%d', doi='%s', arxiv_id='%s')>" % (
            self.id,
            self.doi,
            self.arxiv_id,
        )

    def json_api_repr(self):
        """
        Dict to dump for the JSON API.
        """
        relationships = [a.relationship.name for a in self.related_to]
        return {
            "types": self.__tablename__,
            "id": self.id,
            "attributes": {
                "doi": self.doi,
                "arxiv_id": self.arxiv_id,
            },
            "links": {
                "self": "/papers/%d" % (self.id,)
            },
            "relationships": {
                k: {
                    "links": {
                        "related": (
                            "/papers/%d/relationships/%s?reverse={reverse}" %
                            (self.id, k)
                        )
                    }
                }
                for k in relationships
            }
        }


class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True)
    associations = sqlalchemy_relationship("Association",
                                           back_populates="relationship")
