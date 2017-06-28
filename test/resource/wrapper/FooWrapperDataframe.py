"""
Module containing the FooWrapper1 class
"""
from wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper

import pandas


class FooWrapperDataframe(ToolWrapper):
    """
    This class has been done for example/testing purpose.
    Modifications may lead to failure in tests.
    """
    __mapper_args__ = {'polymorphic_identity': "FooWrapperDataframe"}

    def specify_output_table(self):
        return ["FooBase"]

    def run(self):
        d = {
            'id': [0, 1, 2, 3, 4],
            'name': [
                "FooWrapperDataframe 0",
                "FooWrapperDataframe 1",
                "FooWrapperDataframe 2",
                "FooWrapperDataframe 3",
                "FooWrapperDataframe 4"
            ]
        }

        df = pandas.DataFrame(d)
        self.session().pandas_to_sql(df, self.output_table("FooBase").__tablename__, if_exists="append", index=False)

        result_df = self.session().pandas_read_sql("SELECT * FROM " + self.output_table("FooBase").__tablename__ + ";")

        if len(result_df) != 5:
            raise Exception("The FooWrapperDataframe didn't insert rows correctly")

