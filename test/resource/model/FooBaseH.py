"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, Integer, String

from wopmars.Base import Base


class FooBaseH(Base):
    """
    Documentation for the class
    """

    __tablename__ = "FooBaseH"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    state = Column(String)

    __mapper_args__ = {
        'polymorphic_on': state,
        'polymorphic_identity': "1"
    }
