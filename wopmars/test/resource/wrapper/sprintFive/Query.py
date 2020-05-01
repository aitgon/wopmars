import threading

from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.utils.Logger import Logger


class Query(ToolWrapper):
    __mapper_args__ = {'polymorphic_identity': "sprintFive.Query"}

    def specify_input_table(self):
        return ["FooBase"]

    def run(self):
        Logger.instance().info(threading._active)
        self.session.query(self.input_table("FooBase")).all()
