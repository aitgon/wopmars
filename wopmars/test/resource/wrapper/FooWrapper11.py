"""
Module containing the FooWrapper1 class
"""
import subprocess
import time

from wopmars.utils.Logger import Logger
from wopmars.models.ToolWrapper import ToolWrapper


class FooWrapper11(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper11"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_file(self):
        return ["output1", "output2", "output3"]

    def run(self):
        Logger.instance().info(self.__class__.__name__ + " is running...")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        p2 = subprocess.Popen(["touch", self.output_file("output2")])
        p2.wait()
        p3 = subprocess.Popen(["touch", self.output_file("output3")])
        p3.wait()
        time.sleep(0.1)
