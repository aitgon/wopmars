"""
Module containing the FooWrapper1 class
"""

import subprocess
import time

from wopmars.utils.Logger import Logger
from wopmars.models.ToolWrapper import ToolWrapper


class FooWrapper5(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "fooPackage.FooWrapper5"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_file(self):
        return ["output1"]

    def specify_output_table(self):
        return ["FooBaseP"]

    def run(self):
        Logger.instance().info(self.__class__.__name__ + " is running...")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        for i in range(10):
            f = self.output_table("FooBaseP")(name="Foowrapper5 - " + str(i))
            self.session.add(f)
        self.session.commit()
        time.sleep(1)
