"""
Module containing the FooWrapper1 class
"""
from wopmars.models.ToolWrapper import ToolWrapper


class FooWrapperH(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {
        "polymorphic_identity": "FooWrapperH"
    }

    def specify_input_table(self):
        return ["FooBaseH"]

    def specify_output_table(self):
        return ["FooBaseH"]

    def run(self):
        q = self.session.query(self.input_table("FooBaseH")).all()
        for r in q:
            r.name2="FooBaseH2 - " + str(r.id)
            self.session.add(r)
        self.session.commit()
