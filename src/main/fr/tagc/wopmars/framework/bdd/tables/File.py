"""
Module containing the File class.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class File(Base):
    __tablename__ = "file"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    path = Column(String)

    # One file is in Many rule_file and is in Many rule
    rules = relationship("RuleFile", back_populates="file")
