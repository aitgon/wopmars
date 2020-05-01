"""
Module containing the FooWrapper2 class
"""
from wopmars.models.ToolWrapper import ToolWrapper


class FooWrapper3(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    def specify_input_file(self):
        return ["input1"]

    def specify_input_table(self):
        return ["FooBase"]

    def specify_output_file(self):
        return ["output1"]

    def specify_output_table(self):
        return ["FooBase"]

    def specify_params(self):
        return {"param1": "float|required"}
