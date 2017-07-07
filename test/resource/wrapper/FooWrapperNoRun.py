"""
Module containing the FooWrapper1 class
"""
from wopmars.framework.database.tables.ToolWrapper import ToolWrapper


class FooWrapperNoRun(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapperNoRun"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_file(self):
        return ["output1"]

    def run(self):
        pass
