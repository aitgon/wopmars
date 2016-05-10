"""
Example of module documentation which can be
multiple-lined
"""
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper


class FooWrapper3(ToolWrapper):
    """
    Documentation for the class
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
        return {"param1": ""}
        # TODO get_options
