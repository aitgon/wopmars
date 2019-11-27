"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from wopmars.Base import Base


class FooBase6(Base):
    """
    Documentation for the class
    """
    __tablename__ = "FooBase6"

    id = Column(Integer, primary_key=True)

    foobase3 = relationship("FooBase3", back_populates="foobase6")