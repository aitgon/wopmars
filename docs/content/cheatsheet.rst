Cheat Sheet
============

SQLAlchemy URLs
-----------------

Sqlite, MariaDB/MySQL or PostgreSQL

.. code-block:: bash

    sqlite:///db.sqlite
    mysql://wopuser:mypass@localhost/wopdb
    postgresql://wopuser:mypass@localhost/wopdb


Wopfile or definition file example
----------------------------------

.. code-block:: python


    rule Rule2:
        tool: 'wopexample.wrapper.CarAssembler'
        input:
            table:
                piece: 'wopexample.model.Piece'
        output:
            table:
                piece_car: 'wopexample.model.PieceCar'
        params:
            # The price have to be under 2000!
            max_price: 2000

Wrapper file example
--------------------

For the complete code, go to the github repository

.. code-block:: python

    from wopmars.framework.database.tables.Rule import Rule
    ...

    class CarAssembler(Rule):
        __mapper_args__ = {
            "polymorphic_identity": "wopmars.example.CarAssembler"
        }

        def specify_output_file(self):
            if not self.option("to_file"): # field depends on boolean par
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

            max_price = self.option("max_price") # price threshold

            wheels = session.query(Piece).filter(Piece.type == "wheel").all()
            ...

            s = "car_serial_number, bodywork_serial_number, engine_serial_number, wheel_serial_number, price\n"

            for w in wheels:
                ...
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
                ...
            else:
                session.commit()
    ...

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

    session = self.session()
    engine = session._WopMarsSession__session.bind
    conn = engine.connect()
    mytable_model = self.output_table(MyWrapper.__output_table_mytable)
    myobj = {'atr1': 'val1'}
    try:  # checks if exists myobj in db
        session.query(mytable_model).filter_by(**myobj).one()
    except:  # if not, add
        session.add(mytable_model(**myobj))
    session.commit()




