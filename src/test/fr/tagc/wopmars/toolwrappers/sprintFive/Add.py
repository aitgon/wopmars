from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper


class Add(ToolWrapper):
    __mapper_args__ = {'polymorphic_identity': "sprintFive.Add"}

    def get_input_file(self):
        return ["input1"]

    def get_output_table(self):
        return ["FooBase"]

    def get_params(self):
        return {"rows": "required|int", "del": "bool"}

    def run(self):
        if self.option("del"):
            self.session().delete_content(self.output_table("FooBase"))
        for i in range(self.option("rows")):
            self.session().add(self.output_table("FooBase")(name="Add" + str(i)))

        self.session().commit()
