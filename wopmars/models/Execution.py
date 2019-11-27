from sqlalchemy import Column, Integer, Float, String, BigInteger, DateTime
from sqlalchemy.orm import relationship

from wopmars.Base import Base

class Execution(Base):
    """
    The execution table is a counter of the executions. It allows to discriminate one execution from one other.

    If 2 executions are exactly the same, they will be both stocked in the database with different execution ids.
    The table ``wom_execution`` contains the following fields:

    - id: INTEGER: primary key - auto increment - arbitrary iD
    - started_epoch_millis: BigInteger - unix time at wich the execution started
    - finish_epoch_millis: BigInteger - unix time at wich the execution finished
    - time: FLOAT - the total time of execution
    - status: VARCHAR(255) - the final status of the Execution. it can be:

        - SUCCESS
        - ERROR

    """

    __tablename__ = "wom_execution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_epoch_millis = Column(DateTime, nullable=True)
    finish_epoch_millis = Column(DateTime, nullable=True)
    time = Column(Float, nullable=True)
    status = Column(String(255), nullable=True)

    # One execution has many rules
    rules = relationship("Rule", back_populates="execution")

