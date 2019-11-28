"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from wopmars.Base import Base


class FooBase7(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase7"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255))

    def __repr__(self):
        s = ""
        s += "<FooBase7 (id: %s; is_input: %s)>" % (self.id, self.name)
        return s
