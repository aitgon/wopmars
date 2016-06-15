"""
Module containing the RuleTable class.
"""
from src.main.fr.tagc.wopmars.framework.bdd.Base import Base

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class RuleTable(Base):
    __tablename__ = "rule_table"

    rule_id = Column(Integer, ForeignKey("rule.id"), primary_key=True)
    table_id = Column(Integer, ForeignKey("table.id"), primary_key=True)
    type_id = Column(Integer, ForeignKey("type.id"), primary_key=True)

    # One rule_table has One type
    type = relationship("Type", back_populates="ruletables")

    # One rule_table has One table
    table = relationship("IODbPut", back_populates="rules")
    # One rule_table has One rule
    rule = relationship("ToolWrapper", back_populates="tables", enable_typechecks=False)

    def __repr__(self):
        return str(self.table)