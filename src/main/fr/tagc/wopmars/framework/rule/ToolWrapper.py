"""
This module contains the ToolWrapper class
"""


class ToolWrapper:
    """
    The class ToolWrapper is the superclass of the Wrapper which
    will be designed by the users.
    """    
    def __init__(self, inputSet=None, outputSet=None, optionSet=None):
        """
        The constructor
        
        More documentation
        :param inputSet: ObjectSet([IOPUT])
        :param outputSet: ObjectSet([IOPUT])
        :param optionSet: ObjectSet([Option])
        :return: void
        """
        self.__inputSet = inputSet
        self.__outputSet = outputSet
        self.__optionSet = optionSet

    def __eq__(self, other):
        """
        Two ToolWrapper objects are equals if their attributes are equals
        :param other:
        :return:
        """
        # print(self, other)
        # print(1, self.__inputSet == other.get_input_set(), "\n",
        #       2, self.__outputSet == other.get_output_set(), "\n",
        #       3, self.__optionSet == other.get_option_set())

        return (self.__inputSet == other.get_input_set() and
                self.__outputSet == other.get_output_set() and
                self.__optionSet == other.get_option_set())
        # TODO verifier si ce test passe

    def __hash__(self):
        """
        Redefining the hash method allows ToolWrapper objects to be indexed in sets and dict
        :return:
        """
        return id(self)

    def get_input_set(self):
        return self.__inputSet

    def get_output_set(self):
        return self.__outputSet

    def get_option_set(self):
        return self.__optionSet

    # TODO verify that important methods have not been overwritten by the user