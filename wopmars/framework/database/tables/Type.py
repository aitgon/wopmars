from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from wopmars.framework.database.Base import Base


class Type(Base):
    """
    This class is the model of the table ``wom_type``. It stores the two kind of entry named "input" and "output" which
    are associated with an ID.

    Fields:

    - id: INTEGER - primary key -arbitrary ID
    - name: VARCHAR(255) - the name of the type ("input" or "output")
    """
    __tablename__ = "wom_type"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))

    # One type is in Many table
    tables = relationship("IODbPut", back_populates="type")
    # One type is in Many files
    files = relationship("IOFilePut", back_populates="type")

    def __repr__(self):
        return "<Type: %s>" % self.name
