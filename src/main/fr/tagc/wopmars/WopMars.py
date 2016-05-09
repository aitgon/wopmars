"""
Main module of the product, entry-point.
"""
from src.main.fr.tagc.wopmars.framework.parsing.Parser import Parser


class WopMars:
    """
    Documentation for the class
    """
    def __init__(self):
        self.__s_workflow_definition_filename = "path/to/the/file"

    def run(self):
        """
        Entry-point of the program
        """
        parser = Parser()
        parser.parse()


if __name__ == "__main__":
    WopMars().run()
