Overview
============

A Wopmars workflow requires the definition of three types of files:

- The workflow definition file or wopfile
- The tool wrappers
- The models


The *wopfile* defines the rules to convert inputs into outputs based on a tool:

.. code-block:: yaml

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wopexample.wrappers.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'wopexample.models.Piece'

The value of the tool field are python paths to classes called *wrappers* compatible with WoPMaRS. These wrapper classes are able to process inputs and outputs.

.. code-block:: python

    from wopmars.main.tagc.framework.bdd.tables.ToolWrapper import ToolWrapper # required import

    class SparePartsManufacturer(ToolWrapper): # required class definition
        __mapper_args__ = {'polymorphic_identity': __name__} # required line
        # my I/O vars
        __input_file_piece = "piece"
        __output_table_piece = "piece"

        def specify_input_file(self):
            # defines input piece file field in previous workflow definition
            return [SparePartsManufacturer.__input_file_piece]

        def specify_output_table(self):
            # defines output piece table field in previous workflow definition
            return [SparePartsManufacturer.__output_table_piece]

        def run(self):
            session = self.session() # inherit session
            piece_path = self.input_file(SparePartsManufacturer.__input_file_piece) # string
            piece_m = self.output_table(SparePartsManufacturer.__output_table_piece) # model class
            with open(piece_path, "r") as fin:
                for line_str in fin.readlines():
                    line_str = line_str.strip()
                    line_list = line_str.split("\t")
                    serial_number = line_list[0]
                    typee = line_list[1]
                    price = line_list[2]
                    try: # check if exists
                        session.query(piece_m).filter_by(serial_number=serial_number, type2=typee, price=price).one()
                    except: # if not commit
                        instance = piece_m(serial_number=serial_number, type2=typee, price=price)
                        session.add(instance)
                    session.commit()


Input or output fields can contain *file* fields with normal file paths or *table* fields. The values of *table* fields are python paths to SQL Alchemy models in the PYTHONPATH:

.. code-block:: python

    from wopmars.main.tagc.framework.bdd.Base import Base
    from sqlalchemy import Column, Integer, String, Float

    class Piece(Base):
        __tablename__ = "piece"

        id = Column(Integer, primary_key=True, autoincrement=True)
        serial_number = Column(String(255), unique=True)
        type2 = Column(String(255))
        price = Column(Float)

We recomend to organize wrappers and models for a particular aim in a python package to simplify development and installation of wrappers and classes.

.. code-block:: shell

    .
    └── wopmars_example
        ├── input
        │   └── pieces.txt
        ├── output
        ├── setup.py
        ├── wopexample
        │   ├── __init__.py
        │   ├── models
        │   │   ├── __init__.py
        │   │   ├── PieceCar.py
        │   │   └── Piece.py
        │   └── wrappers
        │       ├── CarAssembler.py
        │       ├── __init__.py
        │       └── SparePartsManufacturer.py
        └── Wopfile

After defining wrappers and modes in a dedicated python package and installing it you can run the workflow using a commands

.. code-block:: shell

wopmars ....

Now that you should understand the basics of WoPMaRS, I recommand you to go to the quick start section to try a working example.


