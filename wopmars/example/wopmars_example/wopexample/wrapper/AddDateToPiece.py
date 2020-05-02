import time, datetime
import random

from wopmars.models.ToolWrapper import ToolWrapper


class AddDateToPiece(ToolWrapper):
    __mapper_args__ = {
        "polymorphic_identity": __module__
    }

    def specify_input_table(self):
        return ["piece"]

    def specify_output_table(self):
        return ["piece"]

    def run(self):
        session = self.session
        DatedPiece = self.output_table("piece")

        for p in self.session.query(DatedPiece).all():
            date = datetime.datetime.fromtimestamp(time.time() - random.randint(1000000, 100000000))
            p.date = date
            session.add(p)
        session.commit()