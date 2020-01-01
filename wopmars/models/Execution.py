from sqlalchemy import Column, Integer, Float, String, BigInteger, DateTime
from sqlalchemy.orm import relationship

from wopmars.Base import Base

class Execution(Base):
    """
    The execution table is a counter of the executions. It allows to discriminate one execution from one other.

    If 2 executions are exactly the same, they will be both stocked in the database with different execution ids.
    The table ``wom_Execution`` contains the following fields:

    - id: INTEGER: primary key - auto increment - arbitrary iD
    - started_at: BigInteger - unix mtime_epoch_millis at wich the execution started
    - finished_at: BigInteger - unix mtime_epoch_millis at wich the execution finished
    - mtime_epoch_millis: FLOAT - the total mtime_epoch_millis of execution
    - status: VARCHAR(255) - the final status of the Execution: FINISHED, ERROR
    """

    __tablename__ = "wom_{}".format(__qualname__)

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    time = Column(Float, nullable=True)
    status = Column(String(255), nullable=True)

    # One execution has many rules
    # rules = relationship("ToolWrapper", back_populates="execution")
    relation_execution_to_toolwrapper = relationship("ToolWrapper", back_populates="relation_toolwrapper_to_execution", cascade="all, delete, delete-orphan")

