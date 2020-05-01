from wopmars.models import ToolWrapper


class AddWithOrWithoutDeleteBefore(ToolWrapper):
    __mapper_args__ = {'polymorphic_identity': "sprintFive.AddWithOrWithoutDeleteBefore"}

    def specify_input_file(self):
        return ["input1"]

    def specify_output_table(self):
        return ["FooBase", "FooBase2"]

    def run(self):
        self.session.delete_content(self.output_table("FooBase"))
        for i in range(100):
            self.session.add(self.output_table("FooBase")(name="DeleteThenAdd" + str(i)))
            self.session.add(self.output_table("FooBase2")(name="Add.py" + str(i)))

        self.session.commit()
