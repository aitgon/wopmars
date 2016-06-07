"""
Module containing the FooWrapper1 class
"""
import os

from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
import time


class FooWrapper8(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """    
    def get_input_file(self):
        return ["input1"]

    def get_output_file(self):
        return ["output1"]

    def run(self):
        print(self.__class__.__name__ + " en cours d'exécution.")
        time.sleep(1)
        print("Ecriture de " + self.output("output1"))
        os.system("touch " + self.output("output1"))
        pass
