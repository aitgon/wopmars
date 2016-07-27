"""
Module containing the ModificationTable class.
"""
from wopmars.main.tagc.framework.bdd.Base import Base
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship


class ModificationTable(Base):
    """
    class ModificationTable
    """

    __tablename__ = "wom_modification_table"

    table_name = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)

    tables = relationship("IODbPut", back_populates="modification")

    def __repr__(self):
        return "<Modification on " + str(self.table_name) + ": " + str(self.date) + ">"