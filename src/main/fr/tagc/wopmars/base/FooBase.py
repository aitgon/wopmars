"""
Example of module documentation which can be
multiple-lined
"""
from fr.tagc.wopmars.base.Base import Base
from sqlalchemy import Column, Integer


class FooBase(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase"

    id = Column(Integer, primary_key=True)