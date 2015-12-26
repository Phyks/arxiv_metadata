"""
This file contains the database schema in SQLAlchemy format.
"""
import sqlite3

from sqlalchemy import event
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship as sqlalchemy_relationship

Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Auto enable foreign keys for SQLite.
    """
    # Play well with other DB backends
    if type(dbapi_connection) is sqlite3.Connection:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class RelationshipAssociation(Base):
    # Relationships are to be read "left RELATION right"
    __tablename__ = "relationship_association"
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

tag_association_table = Table(
    'tag_association', Base.metadata,
    Column('paper_id', Integer, ForeignKey('papers.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
)


class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True)
    doi = Column(String(), nullable=True, unique=True)
    arxiv_id = Column(String(30), nullable=True, unique=True)
    # related_to are papers related to this paper (this_paper R …)
    related_to = sqlalchemy_relationship("RelationshipAssociation",
                                         foreign_keys="RelationshipAssociation.left_id",
                                         back_populates="left_paper",
                                         passive_deletes=True)
    # related_by are papers referenced by this paper (… R this_paper)
    related_by = sqlalchemy_relationship("RelationshipAssociation",
                                         foreign_keys="RelationshipAssociation.right_id",
                                         back_populates="right_paper",
                                         passive_deletes=True)
    # Tags relationship
    tags = sqlalchemy_relationship("Tag",
                                   secondary=tag_association_table,
                                   backref="papers",
                                   passive_deletes=True)

    def __repr__(self):
        return "<Paper(id='%d', doi='%s', arxiv_id='%s')>" % (
            self.id,
            self.doi,
            self.arxiv_id,
        )

    def json_api_repr(self, db):
        """
        Dict to dump for the JSON API.
        """
        relationships = [i.name for i in db.query(Relationship).all()]
        relationships_dict = {
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
        relationships_dict["tags"] = {
            "links": {
                "related": "/papers/%d/relationships/tags" % (self.id,)
            }
        }
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
            "relationships": relationships_dict
        }


class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True)
    associations = sqlalchemy_relationship("RelationshipAssociation",
                                           back_populates="relationship",
                                           passive_deletes=True)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(), unique=True)

    def json_api_repr(self):
        """
        Dict to dump for the JSON API.
        """
        return {
            "types": self.__tablename__,
            "id": self.id,
            "attributes": {
                "name": self.name,
            },
            "links": {
                "self": "/tags/%d" % (self.id,)
            }
        }


class CitationProcessingQueue(Base):
    __tablename__ = "citationprocessingqueue"
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer,
                      ForeignKey('papers.id', ondelete="CASCADE"),
                      unique=True)
    paper = sqlalchemy_relationship("Paper")
