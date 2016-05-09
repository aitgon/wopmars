"""
Example of module documentation which can be
multiple-lined
"""


class ParsingException(Exception):
    """
    Documentation for the class
    """    
    def __init__(self, message):
        """
        First line short documentation
        
        More documentation
        :param something:
        :return:
        """
        self.__message = message

    def __str__(self):
        s = "Error while parsing the configuration file: \n\t" + "\n\t".join(self.__message.split("\n"))
        return s