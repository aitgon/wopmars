"""
Module containing the Type class.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Type(Base):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    # One type is in Many rule_table
    ruletables = relationship("RuleTable", back_populates="type")
    # One type is in Many rule_file
    rulefiles = relationship("RuleFile", back_populates="type")