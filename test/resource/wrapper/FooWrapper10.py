"""
Module containing the FooWrapper1 class
"""
import time

import subprocess

from wopmars.framework.database.tables.ToolWrapper import ToolWrapper


class FooWrapper10(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper10"}

    def specify_input_file(self):
        return ["input1", "input2", "input3"]

    def specify_output_file(self):
        return ["output1"]

    def run(self):
        print(self.__class__.__name__ + " is running...")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        time.sleep(1)
