"""
Module containing the FooWrapper1 class
"""

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapperNoTable(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """    
    def get_input_table(self):
        return ["failure"]


