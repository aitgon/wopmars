"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class FooBase(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase"

    id = Column(Integer, primary_key=True)