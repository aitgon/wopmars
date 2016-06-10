"""
Module containing the Table class.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Table(Base):
    __tablename__ = "table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)

    # One table is in Many rule_table
    rules = relationship("RuleTable", back_populates="table")

    def __repr__(self):
        return "<Table (name='%s')>" % (self.name)