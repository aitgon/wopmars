Cheat Sheet
============

Wopfile or definition file example
----------------------------------

.. code-block:: python

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wrapper.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'model.Piece'

    # CarAssembler make the combinations of all possible pieces to build cars and calculate the final price
    rule Rule2:
        tool: 'wrapper.CarAssembler'
        input:
            table:
                piece: 'model.Piece'
        output:
            table:
                piece_car: 'model.PieceCar'
        params:
            # The price have to be under 2000!
            max_price: 2000


Wrapper file example
--------------------

For the complete code, go to the github repository

.. code-block:: python

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


Model file example
--------------------

.. code-block:: python

    from wopmars.framework.database.Base import Base

    from sqlalchemy import Column, Integer, String, Float


    class Piece(Base):
        __tablename__ = "piece"

        id = Column(Integer, primary_key=True, autoincrement=True)
        serial_number = Column(String, unique=True)
        type = Column(String)
        price = Column(Float)


Database access examples
--------------------------

ORM query and insert

.. code-block:: python

    session = self.session
    engine = session._WopMarsSession__session.bind
    conn = engine.connect()
    mytable_model = self.output_table(MyWrapper.__output_table_mytable)
    myobj = {'atr1': 'val1'}
    try:  # checks if exists myobj in db
        session.query(mytable_model).filter_by(**myobj).one()
    except:  # if not, add
        session.add(mytable_model(**myobj))
    session.commit()




