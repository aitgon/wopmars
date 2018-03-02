"""
Module containing the FooWrapper1 class
"""
import subprocess

from wopmars.framework.database.tables.ToolWrapper import ToolWrapper


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
        print(self.__class__.__name__ + " is running...")
        p = subprocess.Popen(["touch", self.output_file("output1")])
        p.wait()
        # self.session().delete_content(self.output_table("FooBase"))
        for i in range(1000):
            f = self.output_table("FooBase")(name="Foowrapper5 - " + str(i))
            self.session().add(f)
        self.session().commit()
        self.log("info", "coucou")
        self.log("warning", "coucou")
        self.log("error", "coucou")
        self.log("debug", "coucou")
