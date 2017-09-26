"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from wopmars.framework.database.Base import Base


class FooBase(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))

    def __repr__(self):
        s = ""
        s += "<FooBase (id: %s; name: %s)>" % (self.id, self.name)
        return s
