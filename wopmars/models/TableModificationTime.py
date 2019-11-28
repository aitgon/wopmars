from wopmars.Base import Base
from sqlalchemy import Column, String, BigInteger
from sqlalchemy.orm import relationship


class TableModificationTime(Base):
    """
    The TableModificationTime model contains the table names of the workflow and their mtime_epoch_millis of last modification. The table
    ``wom_modification_table`` contains the following fields:

    - table_name: VARCHAR(255) - primary key - the is_input of the table
    - mtime_epoch_millis: INTEGER - unix mtime_epoch_millis [ms] of last modification of the table
    """

    __tablename__ = "wom_modification_table"

    table_name = Column(String(255), primary_key=True)
    mtime_epoch_millis = Column(BigInteger, nullable=False)

    tables = relationship("TableInputOutputInformation", back_populates="modification")

    def __repr__(self):
        return "<Modification on " + str(self.table_name) + ": " + str(self.mtime_epoch_millis) + ">"
