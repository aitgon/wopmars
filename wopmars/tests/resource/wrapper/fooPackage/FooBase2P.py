"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from wopmars.Base import Base


class FooBase2P(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase2P"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))