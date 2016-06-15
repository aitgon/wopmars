"""
Module containing the FooWrapper1 class
"""
import os
import time

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapper10(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """    
    def get_input_file(self):
        return ["input1", "input2"]

    def get_output_file(self):
        return ["output1"]