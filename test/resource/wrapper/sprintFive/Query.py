import threading

from wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class Query(ToolWrapper):
    __mapper_args__ = {'polymorphic_identity': "sprintFive.Query"}

    def specify_input_table(self):
        return ["FooBase"]

    def run(self):
        print(threading._active)
        self.session().query(self.input_table("FooBase")).all()
