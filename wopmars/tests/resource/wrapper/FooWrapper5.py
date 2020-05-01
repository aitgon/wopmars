"""
Module containing the FooWrapper1 class
"""
import subprocess

from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.utils.Logger import Logger

class FooWrapper5(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper5"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_file(self):
        return ["output1"]

    def specify_output_table(self):
        return ["FooBase"]

    def run(self):
        Logger.instance().info(self.__class__.__name__ + " is running...")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        # self.session.delete_content(self.output_table("FooBase"))
        for i in range(1000):
            # import pdb; pdb.set_trace()
            f = self.output_table("FooBase")(name="Foowrapper5 - {}".format(i))
            self.session.add(f)
        self.session.commit()
