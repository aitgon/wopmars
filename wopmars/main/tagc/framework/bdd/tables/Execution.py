"""
This module contains the Execution table model.
"""
from sqlalchemy import Column, Integer, DateTime, Float, String
from sqlalchemy.orm import relationship

from wopmars.main.tagc.framework.bdd.Base import Base


class Execution(Base):
    """
    The execution table is a counter of the executions. It allows to discriminate one execution from one other.

    If 2 executions are exactly the same, they will be both stocked in the database with different execution numbers.
    The times at which the execution has started and finished are stored (as the the time of the whole execution).
    The status of the execution is stored with "FINISHED" as possible flags.
    """

    __tablename__ = "wom_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    time = Column(Float, nullable=True)
    status = Column(String, nullable=True)

    # One execution has many rules
    rules = relationship("ToolWrapper", back_populates="execution")

