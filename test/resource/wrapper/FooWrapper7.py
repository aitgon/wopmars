"""
Module containing the FooWrapper1 class
"""
import time

from test.resource.model.FooBase2 import FooBase2
from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

class FooWrapper7(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapper7"}

    def specify_input_table(self):
        return ["FooBase"]

    def specify_output_table(self):
        return ["FooBase2"]

    def run(self):
        print(self.__class__.__name__ + " is running...")
        inputs = self.session().query(self.input_table("FooBase")).all()
        self.session().delete_content(self.output_table("FooBase2"))
        for i in inputs:
            entry = self.output_table("FooBase2")(name=i.name)
            self.session().add(entry)
        print(self.session().query(FooBase2).all())
        time.sleep(1)
