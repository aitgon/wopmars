"""
Module containing the FooWrapper1 class
"""

from wopmars.models.ToolWrapper import ToolWrapper


class FooWrapperRelationShip(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapperRelationShip"}

    def specify_output_table(self):
        return ["FooBase3", "FooBase4", "FooBase5", "FooBase6"]

    def run(self):
        for i in range(10):
            f3 = self.output_table("FooBase3")(id=i+1, name="F3 - " + str(i), id_foobase6=i+1)
            f4 = self.output_table("FooBase4")(id_foobase3=i+1, id_foobase5=i+1)
            f5 = self.output_table("FooBase5")(id=i+1)
            f6 = self.output_table("FooBase6")(id=i+1)
            self.session.add_all([f3, f4, f5, f6])
        self.session.commit()
