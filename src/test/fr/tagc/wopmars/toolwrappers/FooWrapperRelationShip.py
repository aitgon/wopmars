"""
Module containing the FooWrapper1 class
"""
import os
import time

from matplotlib.compat import subprocess

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class FooWrapperRelationShip(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapperRelationShip"}

    def get_output_table(self):
        return ["FooBase3", "FooBase4"]

    def run(self):
        for i in range(10):
            f3 = self.output_table("FooBase3")(id= i + 1, name="F3 - " + str(i))
            f4 = self.output_table("FooBase4")(id_foobase3 = i + 1)
            self.session().add_all([f3, f4])
        self.session().commit()