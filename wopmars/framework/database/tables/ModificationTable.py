from wopmars.Base import Base
from sqlalchemy import Column, String, BigInteger
from sqlalchemy.orm import relationship


class ModificationTable(Base):
    """
    The ModificationTable model contains the table names of the workflow and their time of last modification. The table
    ``wom_modification_table`` contains the following fields:

    - table_name: VARCHAR(255) - primary key - the name of the table
    - time: INTEGER - unix time [ms] of last modification of the table
    """

    __tablename__ = "wom_modification_table"

    table_name = Column(String(255), primary_key=True)
    time = Column(BigInteger, nullable=False)

    tables = relationship("IODbPut", back_populates="modification")

    def __repr__(self):
        return "<Modification on " + str(self.table_name) + ": " + str(self.time) + ">"
