"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from wopmars.framework.database.Base import Base


class FooBase3(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase3"

    id = Column(Integer, primary_key=True)
    id_foobase6 = Column(Integer, ForeignKey("FooBase6.id"))
    name = Column(String(255))

    foobase4 = relationship("FooBase4", back_populates="foobase3")
    foobase6 = relationship("FooBase6", back_populates="foobase3")
