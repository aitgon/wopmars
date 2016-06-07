"""
Module containing the FooWrapper1 class
"""
import os

from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
import time

from src.main.fr.tagc.wopmars.utils.Logger import Logger


class FooWrapper8(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """    
    def get_input_file(self):
        return ["input1"]

    def get_output_file(self):
        return ["output1"]

    def get_input_table(self):
        return ["FooBase"]

    def get_output_table(self):
        return ["FooBase"]

    def run(self):
        Logger().info(self.__class__.__name__ + " en cours d'exécution.")
        time.sleep(1)
        Logger().info("Ecriture de " + self.output_file("output1"))
        os.system("touch " + self.output_file("output1"))
        Logger().info("Remplissage de la table " + str(self.input_table("FooBase")))
        self.session().add(self.input_table("FooBase")(name="kiki"))
        self.session().add(self.input_table("FooBase")(name="kika"))
        self.session().add(self.input_table("FooBase")(name="kiku"))
        self.session().commit()
