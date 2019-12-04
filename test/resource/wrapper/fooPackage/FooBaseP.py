"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from wopmars.Base import Base


class FooBaseP(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBaseP"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))

    def __repr__(self):
        s = ""
        s += "<FooBase (id: %s; is_input: %s)>" % (self.id, self.name)
        return s