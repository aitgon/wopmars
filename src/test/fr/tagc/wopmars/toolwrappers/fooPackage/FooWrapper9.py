"""
Module containing the FooWrapper1 class
"""
import os
import time

from matplotlib.compat import subprocess

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapper9(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "fooPackage.FooWrapper9"}
    def get_input_file(self):
        return ["input1"]

    def get_input_table(self):
        return ["FooBase2P"]

    def get_output_file(self):
        return ["output1"]

    def run(self):
        print(self.__class__.__name__ + " en cours d'exécution.")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        time.sleep(1)