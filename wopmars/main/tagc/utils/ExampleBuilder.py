import string
import random
import os


class ExampleBuilder:
    def build(self):
        self.build_file_architecture()
        self.create_wopfile()
        self.create_input_file()
        self.create_package()

    def build_file_architecture(self):
        if not os.path.exists("wopmars_example"):
            os.mkdir("wopmars_example")
        if not os.path.exists("wopmars_example/input"):
            os.mkdir("wopmars_example/input")
        if not os.path.exists("wopmars_example/output"):
            os.mkdir("wopmars_example/output")
        if not os.path.exists("wopmars_example/wopexample"):
            os.mkdir("wopmars_example/wopexample")
        if not os.path.exists("wopmars_example/wopexample/wrappers"):
            os.mkdir("wopmars_example/wopexample/wrappers")
        if not os.path.exists("wopmars_example/wopexample/models"):
            os.mkdir("wopmars_example/wopexample/models")

    def create_wopfile(self):
        s = """
rule Rule1:
    tool: 'wopexample.wrappers.SparePartsManufacturer'
    input:
        file:
            pieces: 'input/pieces.txt'
    output:
        table:
            piece: 'wopexample.models.Piece'

rule Rule2:
    tool: 'wopexample.wrappers.CarAssembler'
    input:
        table:
            piece: 'wopexample.models.Piece'
    output:
        table:
            piece_car: 'wopexample.models.PieceCar'
    params:
        max_price: 2000
"""
        with open("wopmars_example/Wopfile", 'w') as fw:
            fw.write(s.strip())

    def create_package(self):
        open("wopmars_example/wopexample/__init__.py", 'a').close()
        open("wopmars_example/wopexample/wrappers/__init__.py", 'a').close()
        open("wopmars_example/wopexample/models/__init__.py", 'a').close()
        CarAssembler = """
import random
import string

from wopmars.main.tagc.framework.bdd.tables.ToolWrapper import ToolWrapper


class CarAssembler(ToolWrapper):
    __mapper_args__ = {
        "polymorphic_identity": "wopmars.example.CarAssembler"
    }

    def specify_input_table(self):
        return ["piece"]

    def specify_output_table(self):
        return ["piece_car"]

    def specify_params(self):
        return {
            "max_price": "int",
        }

    def run(self):
        session = self.session()
        Piece = self.input_table("piece")
        Piece_car = self.output_table("piece_car")

        max_price = self.option("max_price")

        wheels = session.query(Piece).filter(Piece.type == "wheel").all()
        engines = session.query(Piece).filter(Piece.type == "engine").all()
        bodyworks = session.query(Piece).filter(Piece.type == "bodywork").all()
        uniques_serials = [s[0] for s in session.query(Piece.serial_number).all()]

        for w in wheels:
            for e in engines:
                for b in bodyworks:
                    car_serial_number = CarAssembler.id_generator()
                    while car_serial_number in uniques_serials:
                        car_serial_number = CarAssembler.id_generator()
                    uniques_serials.append(car_serial_number)
                    price = w.price + e.price + b.price
                    if not max_price or (max_price and price <= max_price):
                        session.add(Piece_car(car_serial_number=car_serial_number,
                                              bodywork_serial_number=b.serial_number,
                                              engine_serial_number=e.serial_number,
                                              wheel_serial_number=w.serial_number,
                                              price=price))

        session.commit()

    @staticmethod
    def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
"""

        with open("wopmars_example/wopexample/wrappers/CarAssembler.py", 'w') as fw:
            fw.write(CarAssembler)

        SparePartsManufacturer = """
from wopmars.main.tagc.framework.bdd.tables.ToolWrapper import ToolWrapper


class SparePartsManufacturer(ToolWrapper):
    __mapper_args__ = {
        "polymorphic_identity": "wopmars.example.SparePartsManufacturer"
    }

    def specify_input_file(self):
        return ["pieces"]

    def specify_output_table(self):
        return ["piece"]

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
            session.add(Piece(serial_number=piece_serial_number, price=piece_price, type=piece_type))

        session.commit()

"""

        with open("wopmars_example/wopexample/wrappers/SparePartsManufacturer.py", 'w') as fw:
            fw.write(SparePartsManufacturer)

        Piece = """
from wopmars.main.tagc.framework.bdd.Base import Base

from sqlalchemy import Column, Integer, String, Float


class Piece(Base):
    __tablename__ = "piece"

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String, unique=True)
    type = Column(String)
    price = Column(Float)
"""
        with open("wopmars_example/wopexample/models/Piece.py", 'w') as fw:
            fw.write(Piece)

        PieceCar = """
from sqlalchemy.sql.schema import ForeignKey

from wopmars.main.tagc.framework.bdd.Base import Base

from sqlalchemy import Column, Integer, String, Float


class PieceCar(Base):
    __tablename__ = "piece_car"

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_serial_number = Column(String, unique=True)
    bodywork_serial_number = Column(String, ForeignKey("piece.serial_number"))
    engine_serial_number = Column(String, ForeignKey("piece.serial_number"))
    wheel_serial_number = Column(String, ForeignKey("piece.serial_number"))
    price = Column(Float)
"""

        with open("wopmars_example/wopexample/models/PieceCar.py", 'w') as fw:
            fw.write(PieceCar)

        setup = """
from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

setup(
    name='wopexample',
    version='1.0',
    description='Simple example for experimenting Wopmars',
    author='Luc Giffon - TAGC',
    author_email='luc.giffon@gmail.com',
    packages=find_packages(),
)
"""
        with open("wopmars_example/setup.py", 'w') as fw:
            fw.write(setup)

    def create_input_file(self):
        s = ""
        types = ["wheel", "bodywork", "engine"]
        uniques = []
        for i in range(20):
            serial = ExampleBuilder.id_generator()
            while serial in uniques:
                serial = ExampleBuilder.id_generator()
            uniques.append(serial)

            s += serial + ";"
            s += types[random.randint(0, 2)] + ";"
            s += "%.2f" % random.uniform(500, 1000) + "\n"

        with open("wopmars_example/input/pieces.txt", 'w') as fw:
            fw.write(s.strip())

    @staticmethod
    def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))