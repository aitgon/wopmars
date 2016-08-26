from sqlalchemy import Column, String

from FooBaseH import FooBaseH


class FooBaseH2(FooBaseH):
    name2 = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': "2"
    }
