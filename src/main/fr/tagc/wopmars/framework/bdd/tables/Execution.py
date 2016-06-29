"""
This module contains the Execution table class
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Execution(Base):
    """
    The execution table is a counter of the executions. It allows to discriminate one execution from one other.

    If 2 executions are exactly the same, they will be both stocked in the database with different execution numbers.
    """

    __tablename__ = "wom_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # One execution has many rules
    rules = relationship("ToolWrapper", back_populates="execution")

