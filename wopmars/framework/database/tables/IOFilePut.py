import os

from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from wopmars.framework.database.Base import Base
from wopmars.framework.database.tables.IOPut import IOPut
from wopmars.utils.Logger import Logger


class IOFilePut(IOPut, Base):
    """
    This class extends IOPut and is specific to the input or output files. It is the model which store the references
    to the actual files needed by the user. The table ``wom_file`` associated with this model contains the
    following fields:

    - id: INTEGER - primary key - autoincrement - arbitrary ID
    - name: VARCHAR(255) - the name of the reference to the file
    - path: VARCHAR(255) - the path to the file
    - rule_id: INTEGER - foreign key to the associated rule ID: :class:`wopmars.framework.database.tables.ToolWrapper.ToolWrapper`
    - type_id: INTEGER - foreign key to the associated type ID: :class:`wopmars.framework.database.tables.Type.Type`
    - used_at: DATE - date at which the table have been used
    - size: INTEGER - the size of the file
    """
    __tablename__ = "wom_file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    path = Column(String(255))
    rule_id = Column(Integer, ForeignKey("wom_rule.id"))
    type_id = Column(Integer, ForeignKey("wom_type.id"))
    used_at = Column(DateTime, nullable=True)
    size = Column(BigInteger, nullable=True)

    # One file is in Many rule_file and is in Many rule
    rule = relationship("ToolWrapper", back_populates="files", enable_typechecks=False)
    # One file has One type
    type = relationship("Type", back_populates="files")

    def is_ready(self):
        """
        Check if the file exists on the system.

        :return: boolean: True if it exists, false if not
        """
        Logger.instance().debug("Checking if " + self.name + " is ready: " + self.path)
        return os.path.isfile(self.path)

    def __eq__(self, other):
        return os.path.abspath(self.path) == os.path.abspath(other.path) and self.name == other.name

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "<File (%s): %s: %s; size: %s; used_at: %s>" % (self.type.name, self.name, self.path, self.size, self.used_at)

    def __str__(self):
        return "file: " + self.name + ": " + self.path
