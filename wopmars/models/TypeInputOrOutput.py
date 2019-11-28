from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from wopmars.Base import Base


class TypeInputOrOutput(Base):
    """
    This class is the model of the table ``wom_type``. It stores the two kind of entry named "input" and "output" which
    are associated with an ID.

    Fields:

    - id: INTEGER - primary key -arbitrary ID
    - name: VARCHAR(255) - the name of the type ("input" or "output")
    """
    __tablename__ = "wom_type_input_or_output"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255))

    # One type is in Many table
    tables = relationship("TableInputOutputInformation", back_populates="type")
    # One type is in Many files
    files = relationship("FileInputOutputInformation", back_populates="type")

    def __repr__(self):
        return "<TypeInputOrOutput: %s>" % self.name
