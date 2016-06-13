"""
Module containing the RuleFile class.
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class RuleFile(Base):
    __tablename__ = "rule_file"

    rule_id = Column(Integer, ForeignKey("rule.id"), primary_key=True)
    file_id = Column(Integer, ForeignKey("file.id"), primary_key=True)
    type_id = Column(Integer, ForeignKey("type.id"), primary_key=True)

    # One rule_file has One type
    type = relationship("Type", back_populates="rulefiles")

    # One rule_file has One file
    file = relationship("File", back_populates="rules")
    # One rule_file has One rule
    rule = relationship("Rule", back_populates="files")