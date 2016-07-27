"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class FooBase3(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase3"

    id = Column(Integer, primary_key=True)
    id_foobase6 = Column(Integer, ForeignKey("FooBase6.id"))
    name = Column(String)

    foobase4 = relationship("FooBase4", back_populates="foobase3")
    foobase6 = relationship("FooBase6", back_populates="foobase3")