"""
Module containing the FooWrapper1 class
"""
import os
import time

from matplotlib.compat import subprocess

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapper12(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper12"}

    def get_output_file(self):
        return ["output1"]

    def get_output_table(self):
        return ["FooBase"]
