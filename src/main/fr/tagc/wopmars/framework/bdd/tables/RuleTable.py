"""
Module containing the RuleTable class.
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class RuleTable(Base):
    __tablename__ = "rule_table"

    rule_id = Column(Integer, ForeignKey("rule.id"), primary_key=True)
    table_id = Column(Integer, ForeignKey("table.id"), primary_key=True)
    type_id = Column(Integer, ForeignKey("type.id"), primary_key=True)

    # One rule_table has One type
    type = relationship("Type", back_populates="ruletables")

    # One rule_table has One table
    table = relationship("Table", back_populates="rules")
    # One rule_table has One rule
    rule = relationship("Rule", back_populates="tables")