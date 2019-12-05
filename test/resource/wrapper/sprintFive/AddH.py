from wopmars.models import ToolWrapper


class AddH(ToolWrapper):
    __mapper_args__ = {'polymorphic_identity': "sprintFive.AddH"}

    def specify_output_table(self):
        return ["FooBaseH"]

    def specify_params(self):
        return {"rows": "required|int", "del": "bool"}

    def run(self):
        if self.option("del"):
            self.session.delete_content(self.output_table("FooBaseH"))
        for i in range(self.option("rows")):
            self.session.add(self.output_table("FooBaseH")(name="Add" + str(i)))

        self.session.commit()
