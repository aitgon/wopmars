import os

from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from wopmars.Base import Base
from wopmars.models.InputOutput import InputOutput
from wopmars.utils.Logger import Logger


class FileInputOutputInformation(InputOutput, Base):
    """
    This class extends IOPut and is specific to the input or output files. It is the model which store the references
    to the actual files needed by the user. The table ``wom_file`` associated with this model contains the
    following fields:

    - id: INTEGER - primary key - autoincrement - arbitrary ID
    - is_input: VARCHAR(255) - the is_input of the reference to the file
    - path: VARCHAR(255) - the path to the file
    - toolwrapper_id: INTEGER - foreign key to the associated rule ID: :class:`wopmars.framework.database.tables.ToolWrapper.ToolWrapper`
    - is_input: INTEGER - foreign key to the associated type ID: :class:`wopmars.framework.database.tables.TypeInputOrOutput.TypeInputOrOutput`
    - mtime_epoch_millis: INTEGER - unix mtime_epoch_millis at which the table have been used
    - size: INTEGER - the size of the file
    """

    __tablename__ = "wom_{}".format(__qualname__)

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_key = Column(String(255))
    path = Column(String(255))
    toolwrapper_id = Column(Integer, ForeignKey("wom_ToolWrapper.id", ondelete='CASCADE'))
    is_input = Column(Boolean, ForeignKey("wom_TypeInputOrOutput.is_input"))
    mtime_human = Column(DateTime, nullable=True)
    mtime_epoch_millis = Column(BigInteger, nullable=True)
    size = Column(BigInteger, nullable=True)

    # One file is in one rule
    relation_file_or_tableioinfo_to_toolwrapper = relationship("ToolWrapper", back_populates="relation_toolwrapper_to_fileioinfo", enable_typechecks=False)
    # One file has one typeio
    relation_file_or_tableioinfo_to_typeio = relationship("TypeInputOrOutput", back_populates="relation_typeio_to_fileioinfo")

    def is_ready(self):
        """
        Check if the file exists on the system.

        :return: boolean: True if it exists, false if not
        """
        Logger.instance().debug("Checking if " + self.file_key + " is ready: " + self.path)
        return os.path.isfile(self.path)

    def __eq__(self, other):
        return os.path.abspath(self.path) == os.path.abspath(other.path) and self.file_key == other.file_key

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "<class File: %s: %s; size: %s; mtime_epoch_millis: %s>" \
               % (self.file_key, self.path, self.size, self.mtime_epoch_millis)

    def __str__(self):
        return "file: " + self.file_key + ": " + self.path
