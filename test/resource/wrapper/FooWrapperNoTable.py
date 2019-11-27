"""
Module containing the FooWrapper1 class
"""

from wopmars.models.Rule import Rule


class FooWrapperNoTable(Rule):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapperNoTable"}

    def specify_input_table(self):
        return ["failure"]


