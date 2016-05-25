"""
Module containing the FooWrapper1 class
"""
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper


class FooWrapper5(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """    
    def get_input_file(self):
        return ["input1"]

    def get_input_db(self):
        return ["inputdb1"]

    def get_output_file(self):
        return ["output1"]

    def get_output_db(self):
        return ["outputdb1"]

    def get_params(self):
        return {"param1": "int"}

