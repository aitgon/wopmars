"""
Module contianing the Option class
"""
from src.main.fr.tagc.wopmars.utils.OptionUtils import OptionUtils


class Option:
    """
    The Option class handle a key and a value and is able to say if
    it is properly formated
    """    
    def __init__(self, key, value):
        """
        :param key: String: the key of the option
        :param value: String: the value of the option
        :return: void
        """
        self.__key = key
        self.__value = value

    def correspond(self, carac):
        """
        Check if the option value correspond to the caracteristics given by the tool wrapper

        :param carac: String contenant les caracteristiques de l'option au format: "carac1|carac2|carc3"
        :return:
        """
        list_splitted_carac = carac.split("|")
        for s_type in list_splitted_carac:
            s_formated_type = s_type.strip().lower()
            if s_formated_type in OptionUtils.static_option_castable:
                try:
                    # Trying to cast the value to the specified type in s_formated_type
                    eval(s_formated_type)(self.__value)
                except ValueError:
                    return False
                    # TODO faire exception parsing exception
        return True

    def __eq__(self, other):
        return self.__value == other.get_value() and self.__key == other.get_key()

    def get_value(self):
        return self.__value

    def get_key(self):
        return self.__key

    def __hash__(self):
        return id(self)