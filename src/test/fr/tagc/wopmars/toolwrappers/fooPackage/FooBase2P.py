"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class FooBase2P(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase2P"

    id = Column(Integer, primary_key=True)
    name = Column(String)