import string
import random
import os

class ExampleBuilder:
    def build(self):
        self.build_file_architecture()
        self.create_wopfile()
        self.create_input_file()

    def build_file_architecture(self):
        if not os.path.exists("wopmars_example"):
            os.mkdir("wopmars_example")
        if not os.path.exists("wopmars_example/input"):
            os.mkdir("wopmars_example/input")
        if not os.path.exists("wopmars_example/output"):
            os.mkdir("wopmars_example/output")

    def create_wopfile(self):
        s = """
rule Rule1:
    tool: 'wopmars.example.SparePartsManufacturer'
    input:
        file:
            pieces: 'input/pieces.txt'
    output:
        table:
            piece: 'wopmars.example.Piece'

rule Rule2:
    tool: 'wopmars.example.CarAssembler'
    input:
        table:
            piece: 'wopmars.example.Piece'
    output:
        table:
            car: 'wopmars.example.Car'
            pieces_by_car: 'wopmars.example.PieceCar'
"""
        with open("wopmars_example/Wopfile", 'w') as fw:
            fw.write(s.strip())

    def create_input_file(self):
        s = ""
        types = ["wheel", "bodywork", "engine"]
        uniques = []
        for i in range(100):
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
    def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))