"""
Module containing the FooWrapper1 class
"""

import time
from wopmars.tests.resource.model import FooBase2
from wopmars.models.ToolWrapper import ToolWrapper

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
        # import pdb; pdb.set_trace()
        inputs = self.session.query(self.input_table("FooBase")).all()
        self.session.delete_content(self.output_table("FooBase2"))
        for i in inputs:
            entry = self.output_table("FooBase2")(name=i.name)
            self.session.add(entry)
        time.sleep(0.1)
