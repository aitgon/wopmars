"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class FooBase3(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase3"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    foobase4 = relationship("FooBase4", back_populates="foobase3")