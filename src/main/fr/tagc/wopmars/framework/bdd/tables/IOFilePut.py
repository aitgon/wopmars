"""
Module containing the IOFilePut class
"""
import os

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOPut import IOPut
from src.main.fr.tagc.wopmars.utils.Logger import Logger


class IOFilePut(IOPut, Base):
    """
    This class extends IOPut and is specific to file input or output
    """
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    path = Column(String)

    # One file is in Many rule_file and is in Many rule
    rules = relationship("RuleFile", back_populates="file")

    def is_ready(self):
        """
        Check if the file exists on the hard drive

        :return: boolean: True if it exists, false if not
        """
        Logger.instance().debug("Checking if " + self.name + " is ready: " + self.path)
        return os.path.isfile(self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "<File: %s: %s>" % (self.name, self.path)
