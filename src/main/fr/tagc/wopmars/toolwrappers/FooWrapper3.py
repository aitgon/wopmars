"""
Example of module documentation which can be
multiple-lined
"""
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper


class FooWrapper3(ToolWrapper):
    """
    Documentation for the class
    """    
    pass

    @staticmethod
    def get_input_file():
        return ["input1", "input2", "input3"]


    @staticmethod
    def get_input_db():
        return ["inputdb1"]


    @staticmethod
    def get_output_file():
        return ["output1"]


    @staticmethod
    def get_output_db():
        return ["outputdb1"]


    @staticmethod
    def get_params():
        return {"param1": ""}
        # TODO get_options