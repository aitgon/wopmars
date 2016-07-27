"""
Module containing the IOFilePut class
"""
import os

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from wopmars.main.tagc.framework.bdd.Base import Base
from wopmars.main.tagc.framework.bdd.tables.IOPut import IOPut
from wopmars.main.tagc.utils.Logger import Logger


class IOFilePut(IOPut, Base):
    """
    This class extends IOPut and is specific to file input or output
    """
    __tablename__ = "wom_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    path = Column(String)
    rule_id = Column(Integer, ForeignKey("wom_rule.id"))
    type_id = Column(Integer, ForeignKey("wom_type.id"))
    used_at = Column(DateTime, nullable=True)
    size = Column(Integer, nullable=True)

    # One file is in Many rule_file and is in Many rule
    rule = relationship("ToolWrapper", back_populates="files", enable_typechecks=False)
    # One file has One type
    type = relationship("Type", back_populates="files")

    def is_ready(self):
        """
        Check if the file exists on the hard drive

        :return: boolean: True if it exists, false if not
        """
        Logger.instance().debug("Checking if " + self.name + " is ready: " + self.path)
        return os.path.isfile(self.path)

    def __eq__(self, other):
        return os.path.abspath(self.path) == os.path.abspath(other.path)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "<File (%s): %s: %s; size: %s; used_at: %s>" % (self.type.name, self.name, self.path, self.size, self.used_at)

    def __str__(self):
        return "file: " + self.name + ": " + self.path
