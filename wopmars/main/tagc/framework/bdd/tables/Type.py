"""
Module containing the Type class.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from wopmars.main.tagc.framework.bdd.Base import Base


class Type(Base):
    __tablename__ = "wom_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    # One type is in Many table
    tables = relationship("IODbPut", back_populates="type")
    # One type is in Many files
    files = relationship("IOFilePut", back_populates="type")

    def __repr__(self):
        return "<Type: %s>" % self.name
