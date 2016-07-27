"""
This module contains the DictUtils class.
"""


class DictUtils:
    """
    Class containing methods that are usefull for dealing with dicts
    """
    @staticmethod
    def elm_of_one_dict_in_one_other(one, other):
        """
        Check if all elements of one dict is in an other.

        :param one: dict
        :param other: dict
        :return: boolean: True if all elements of one are in the other
        """
        if len(set(one.keys()).difference(set(other.keys()))):
            return False
        for elm in one:
            if one[elm] != other[elm]:
                return False
        return True

    @staticmethod
    def at_least_one_value_of_one_in_an_other(one, other):
        for value1 in one.values():
            for value2 in other.values():
                if value1 == value2:
                    return True
        return False

    @staticmethod
    def pretty_repr(d, indent=0):
        s = ""
        for key, value in d.items():
            s += '\t' * indent + str(key) + "\n"
            if isinstance(value, dict):
                s += DictUtils.pretty_repr(value, indent + 1)
            else:
                s += '\t' * (indent + 1) + str(value) + "\n"
        return s

    @staticmethod
    def str_to_dict(dictable_string):
        if dictable_string:
            d = dict(eval(dictable_string))
            return d
