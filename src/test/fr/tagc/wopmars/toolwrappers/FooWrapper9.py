"""
Module containing the FooWrapper1 class
"""
import os

from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
import time


class FooWrapper9(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """    
    def get_input_file(self):
        return ["input1", "input2"]

    def run(self):
        print(self.__class__.__name__ + " en cours d'exécution.")
        print(self.session())
        time.sleep(5)
        print("Suppression de " + self.input("input1") + " et " + self.input("input2") + ".")
        os.remove(self.input("input1"))
        os.remove(self.input("input2"))

