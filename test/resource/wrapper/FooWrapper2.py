"""
Module containing the FooWrapper2 class
"""
import time

import subprocess

from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

class FooWrapper2(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper2"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_file(self):
        return ["output1"]

    def specify_params(self):
        return {"param1": "str"}

    def run(self):
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        time.sleep(1)
