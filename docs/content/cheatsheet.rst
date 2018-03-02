Cheat Sheet
============

SQLAlchemy URLs
-----------------

Sqlite:

.. code-block:: bash

    sqlite:///db.sqlite

MariaDB/MySQL:

.. code-block:: bash

    mysql://wopuser:mypass@localhost/wopdb

PostgreSQL:

.. code-block:: bash

    postgresql://wopuser:mypass@localhost/wopdb

Wopfile or definition file example
----------------------------------

.. code-block:: python

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wopexample.wrapper.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'wopexample.model.Piece'

Wrapper file example
--------------------

.. code-block:: python

   from wopmars.framework.database.tables.ToolWrapper import ToolWrapper


    class SparePartsManufacturer(ToolWrapper):
        __mapper_args__ = {
            "polymorphic_identity": "wopmars.example.SparePartsManufacturer"
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
            session = self.session()
            Piece = self.output_table("piece")

            with open(self.input_file("pieces")) as wr:
                lines = wr.readlines()

            for line in lines:
                splitted_line = line.split(";")
                piece_serial_number = splitted_line[0]
                piece_type = splitted_line[1]
                piece_price = float(splitted_line[2])
                if (self.option("max_price") and self.option("max_price" >= piece_price))                         or self.option("max_price") is None:
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

