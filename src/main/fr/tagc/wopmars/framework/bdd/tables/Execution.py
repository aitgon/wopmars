"""
This module contains the Execution table class
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Execution(Base):
    """
    """

    __tablename__ = "execution"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # One execution has many rules
    rules = relationship("ToolWrapper", back_populates="execution")

