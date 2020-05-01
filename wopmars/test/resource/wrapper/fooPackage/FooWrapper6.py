"""
Module containing the FooWrapper1 class
"""
import time
import subprocess

from wopmars.utils.Logger import Logger
from wopmars.models.ToolWrapper import ToolWrapper


class FooWrapper6(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "fooPackage.FooWrapper6"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_file(self):
        return ["output1", "output2"]

    def run(self):
        Logger.instance().info(self.__class__.__name__ + " is running...")
        p1 = subprocess.Popen(["touch", self.output_file('output1')])
        p2 = subprocess.Popen(["touch", self.output_file('output2')])
        p1.wait()
        p2.wait()
        time.sleep(1)
