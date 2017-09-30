import random
import string

from wopmars.framework.database.tables.ToolWrapper import ToolWrapper


class CarAssembler(ToolWrapper):
    __mapper_args__ = {
        "polymorphic_identity": "wopmars.example.CarAssembler"
    }

    def specify_output_file(self):
        if not self.option("to_file"):
            return []
        else:
            return ["piece_car"]

    def specify_input_table(self):
        return ["piece"]

    def specify_output_table(self):
        if self.option("to_file"):
            return []
        else:
            return ["piece_car"]

    def specify_params(self):
        return {
            "to_file": "bool",
            "max_price": "int",
        }

    def run(self):
        session = self.session()
        Piece = self.input_table("piece")
        if not self.option("to_file"):
            Piece_car = self.output_table("piece_car")

        max_price = self.option("max_price")

        wheels = session.query(Piece).filter(Piece.type == "wheel").all()
        engines = session.query(Piece).filter(Piece.type == "engine").all()
        bodyworks = session.query(Piece).filter(Piece.type == "bodywork").all()
        uniques_serials = [s[0] for s in session.query(Piece.serial_number).all()]

        s = "car_serial_number, bodywork_serial_number, engine_serial_number, wheel_serial_number, price\n"

        for w in wheels:
            for e in engines:
                for b in bodyworks:
                    car_serial_number = CarAssembler.id_generator()
                    while car_serial_number in uniques_serials:
                        car_serial_number = CarAssembler.id_generator()
                    uniques_serials.append(car_serial_number)
                    price = w.price + e.price + b.price
                    if not max_price or (max_price and price <= max_price):
                        if not self.option("to_file"):
                            session.add(Piece_car(car_serial_number=car_serial_number,
                                                  bodywork_serial_number=b.serial_number,
                                                  engine_serial_number=e.serial_number,
                                                  wheel_serial_number=w.serial_number,
                                                  price=price))
                        s += ";".join([car_serial_number,
                                       b.serial_number,
                                       e.serial_number,
                                       w.serial_number,
                                       str(price)]) + "\n"

        if self.option("to_file"):
            file_to_write = open(self.output_file("piece_car"), 'w')
            file_to_write.write(s)
            file_to_write.close()
        else:
            session.commit()

    @staticmethod
    def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
