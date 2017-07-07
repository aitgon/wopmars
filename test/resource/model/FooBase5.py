"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from wopmars.framework.database.Base import Base


class FooBase5(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase5"

    id = Column(Integer, primary_key=True)

    foobase4 = relationship("FooBase4", back_populates="foobase5")