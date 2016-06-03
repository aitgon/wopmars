"""
Module contianing the Option class
"""
from fr.tagc.wopmars.utils.OptionUtils import OptionUtils
from fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


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
        Check if the option value correspond to the type given by the tool wrapper. Throws a WopMarsParsingException if
        not.

        :param carac: String containing the carac of the option in the format: "carac1|carac2|carc3"
        :return:
        """
        # get a list of caracs
        list_splitted_carac = carac.split("|")
        for s_type in list_splitted_carac:
            s_formated_type = s_type.strip().lower()
            # check if the carac is a castable type
            if s_formated_type in OptionUtils.static_option_castable:
                try:
                    # try the cast
                    eval(s_formated_type)(self.__value)
                except ValueError:
                    # if it fails, raise an exception: the type has not been respected
                    raise WopMarsException(4, "The given option value of " + str(self.__key) +
                                                  " should be of type " + s_formated_type)
            else:
                # TODO exception de développeur métier qui a mal fait les choses
                pass

    def __eq__(self, other):
        return self.__value == other.get_value() and self.__key == other.get_key()

    def get_value(self):
        return self.__value

    def get_key(self):
        return self.__key

    def __hash__(self):
        return id(self)