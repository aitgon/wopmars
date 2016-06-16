"""
Module containing the FooWrapper2 class
"""
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapper3(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    def get_input_file(self):
        return ["input1"]

    def get_input_table(self):
        return ["FooBase"]

    def get_output_file(self):
        return ["output1"]

    def get_output_table(self):
        return ["FooBase"]

    def get_params(self):
        return {"param1": "float|required"}
