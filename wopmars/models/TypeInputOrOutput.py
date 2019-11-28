from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from wopmars.Base import Base


class TypeInputOrOutput(Base):
    """
    This class is the model of the table ``wom_type``. It stores the two kind of entry named "input" and "output" which
    are associated with an ID.

    Fields:

    - id: INTEGER - primary key -arbitrary ID
    - is_input: VARCHAR(255) - the is_input of the type ("input" or "output")
    """
    __tablename__ = "wom_type_input_or_output"

    is_input = Column(Boolean, primary_key=True, autoincrement=False)

    # One type is in Many table
    tables = relationship("TableInputOutputInformation", back_populates="type")
    # One type is in Many files
    files = relationship("FileInputOutputInformation", back_populates="type")

    def __repr__(self):
        return "<TypeInputOrOutput: {}>".format(self.is_input)
