from wopmars.framework.database.tables.ToolWrapper import ToolWrapper


class Add(ToolWrapper):
    __mapper_args__ = {'polymorphic_identity': "sprintFive.Add"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_table(self):
        return ["FooBase"]

    def specify_params(self):
        return {"rows": "required|int", "del": "bool"}

    def run(self):
        if self.option("del"):
            self.session().delete_content(self.output_table("FooBase"))
        for i in range(self.option("rows")):
            self.session().add(self.output_table("FooBase")(name="Add" + str(i)))

        self.session().commit()
