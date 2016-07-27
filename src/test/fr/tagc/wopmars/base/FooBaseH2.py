"""
Example of module documentation which can be
multiple-lined
"""
from sqlalchemy import Column, String

from FooBaseH import FooBaseH


class FooBaseH2(FooBaseH):
    """
    Documentation for the class
    """
    name2 = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': "2"
    }
