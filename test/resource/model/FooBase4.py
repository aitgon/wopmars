"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from wopmars.framework.database.Base import Base


class FooBase4(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase4"

    id = Column(Integer, primary_key=True)
    id_foobase3 = Column(Integer, ForeignKey("FooBase3.id"))
    id_foobase5 = Column(Integer, ForeignKey("FooBase5.id"))

    foobase3 = relationship("FooBase3", back_populates="foobase4")
    foobase5 = relationship("FooBase5", back_populates="foobase4")