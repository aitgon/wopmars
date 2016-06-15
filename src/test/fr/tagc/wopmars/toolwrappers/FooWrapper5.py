"""
Module containing the FooWrapper1 class
"""
import time

from matplotlib.compat import subprocess

from FooBase import FooBase
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper

class FooWrapper5(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper5"}
    def get_input_file(self):
        return ["input1"]

    def get_output_file(self):
        return ["output1"]

    def get_output_table(self):
        return ["FooBase"]

    def run(self):
        print(self.__class__.__name__ + " en cours d'exécution.")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        for i in range(10):
            f = self.output_table("FooBase")(name="Foowrapper5 - " + str(i))
            self.session().add(f)
        self.session().commit()
        time.sleep(1)