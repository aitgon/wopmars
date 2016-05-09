"""
This module contains the ToolWrapper class
"""
from src.main.fr.tagc.wopmars.utils.DictUtils import DictUtils


class ToolWrapper:
    """
    The class ToolWrapper is the superclass of the Wrapper which
    will be designed by the users.
    """    
    def __init__(self, input_dict={}, output_dict={}, option_dict={}):
        """
        The constructor
        
        More documentation
        :param input_dict: dict(String: IOPUT)
        :param output_dict: dict(String: IOPUT)
        :param option_dict: dict(String: Option)
        :return: void
        """
        self.__input_dict = input_dict
        self.__output_dict = output_dict
        self.__option_dict = option_dict

    def __eq__(self, other):
        """
        Two ToolWrapper objects are equals if their attributes are equals
        :param other: ToolWrapper
        :return:
        """
        return (DictUtils.all_elm_of_one_dict_in_one_other(self.__input_dict, other.get_input_dict()) and
                DictUtils.all_elm_of_one_dict_in_one_other(self.__output_dict, other.get_output_dict()) and
                DictUtils.all_elm_of_one_dict_in_one_other(self.__option_dict, other.get_option_dict()))


    def __hash__(self):
        """
        Redefining the hash method allows ToolWrapper objects to be indexed in sets and dict
        :return:
        """
        return id(self)

    def get_input_dict(self):
        return self.__input_dict

    def get_output_dict(self):
        return self.__output_dict

    def get_option_dict(self):
        return self.__option_dict

    # TODO verify that important methods have not been overwritten by the user