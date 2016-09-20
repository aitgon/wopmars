"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from wopmars.main.tagc.framework.bdd.Base import Base


class FooBase2(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase2"

    id = Column(Integer, primary_key=True)
    name = Column(String)