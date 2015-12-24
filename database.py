"""
This file contains the database schema in SQLAlchemy format.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Paper(Base):
    __tablename__ = 'papers'
    id = Column(Integer, primary_key=True)
    doi = Column(String(), nullable=True, unique=True)
    arxiv_id = Column(String(25), nullable=True, unique=True)

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
                # TODO
            }
        }
