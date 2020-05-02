from wopmars.models.ToolWrapper import ToolWrapper


class SparePartsManufacturer(ToolWrapper):
    __mapper_args__ = {
        "polymorphic_identity": __module__
    }

    def specify_input_file(self):
        return ["pieces"]

    def specify_output_table(self):
        return ["piece"]

    def specify_params(self):
        return {
            "max_price": int
        }

    def run(self):
        session = self.session
        Piece = self.output_table("piece")

        with open(self.input_file("pieces")) as wr:
            lines = wr.readlines()

        for line in lines:
            splitted_line = line.split(";")
            piece_serial_number = splitted_line[0]
            piece_type = splitted_line[1]
            piece_price = float(splitted_line[2])
            if (self.option("max_price") and self.option("max_price" >= piece_price)) \
                    or self.option("max_price") is None:
                session.add(Piece(serial_number=piece_serial_number, price=piece_price, type=piece_type))

        session.commit()
