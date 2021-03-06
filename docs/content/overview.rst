Overview
============


WopMars is a database-driven workflow manager written in python similar to GNU Makefile or Snakemake.
The difference is that the definition file of WopMars takes into account input/output SQLITE table defined as python
paths to SQLAlchemy models.

A Wopmars workflow requires the definition of three types of files:

- The workflow definition file or wopfile
- The tool wrappers
- The models

The *wopfile* defines the rules to convert inputs into outputs based on a tool:

.. code-block:: yaml

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wrapper.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'model.Piece'

The value of the tool field are python paths to classes called *wrappers* compatible with WopMars. These wrapper classes are able to process inputs and outputs.

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


Input or output fields can contain *file* fields with normal file paths or *table* fields. The values of *table* fields
are python paths to SQL Alchemy models in the PYTHONPATH:

.. code-block:: python

    from wopmars.Base import Base

    from sqlalchemy import Column, Integer, String, Float


    class Piece(Base):
        __tablename__ = "piece"

        id = Column(Integer, primary_key=True, autoincrement=True)
        serial_number = Column(String, unique=True)
        type = Column(String)
        price = Column(Float)


We recomend to organize wrappers and models for a particular aim in a python package to simplify development and
installation of wrappers and classes.

.. code-block:: shell

    wopexample
    |-- Wopfile.yml
    |-- Wopfile2
    |-- Wopfile3
    |-- __init__.py
    |-- bats.sh
    |-- input
    |   `-- pieces.txt
    |-- model
    |   |-- DatedPiece.py
    |   |-- Piece.py
    |   |-- PieceCar.py
    |   |-- __init__.py
    |-- output
    |-- setup.py
    `-- wrapper
        |-- AddDateToPiece.py
        |-- CarAssembler.py
        |-- SparePartsManufacturer.py
        |-- __init__.py

As shown in the next section (Quick start) After defining wrappers and modes in a dedicated python package and
installing it you can run the workflow using a commands

.. code-block:: shell

    wopmars -w Wopfile -D "sqlite:///db.sqlite" -v -p

Now that you should understand the basics components of WopMars, I recommend you to go to the quick start section to
try a working example.

