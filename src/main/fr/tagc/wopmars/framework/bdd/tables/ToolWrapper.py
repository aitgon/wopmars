"""
Module containing the ToolWrapper class.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class ToolWrapper(Base):
    __tablename__ = "toolwrapper"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # One toolwrapper is in Many rules
    rules = relationship("Rule", back_populates="toolwrapper")

    def __repr__(self):
        return "<ToolWrapper (name='%s')>" % (self.name)