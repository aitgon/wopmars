"""
Module containing the FooWrapper1 class
"""
import time

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper

class FooWrapper4(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper4"}
    def get_input_file(self):
        return ["input1"]

    def get_output_file(self):
        return ["output1"]

    def run(self):
        print(self.__class__.__name__ + " en cours d'exécution.")
        time.sleep(1)
