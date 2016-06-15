"""
Module containing the FooWrapper1 class
"""
import os
import time

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper

class FooWrapper7(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper7"}
    def get_input_table(self):
        return ["FooBase"]

    def get_output_table(self):
        return ["FooBase2"]