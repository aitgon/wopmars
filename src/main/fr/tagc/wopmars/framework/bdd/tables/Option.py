"""
Module containing the Option class.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Option(Base):
    __tablename__ = "option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(String)

    rules = relationship("Rule", secondary="rule_option", back_populates="options")

    def __repr__(self):
        return "<Option (name='%s')>" % self.name
