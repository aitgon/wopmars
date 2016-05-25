"""
This module contains the DictUtils class.
"""
from src.main.fr.tagc.wopmars.utils.SetUtils import SetUtils


class DictUtils:
    """
    Class containing methods that are usefull for dealing with dicts
    """
    # TODO: tesunitaire sur cette classe
    @staticmethod
    def elm_of_one_dict_in_one_other(one, other):
        """
        Check if all elements of one dict is in an other.

        :param one: dict
        :param other: dict
        :return: boolean: True if all elements of one are in the other
        """
        if set(one.keys()) != set(other.keys()):
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


if __name__ == "__main__":
    print(DictUtils.elm_of_one_dict_in_one_other({"a": 1}, {"a": 1, "b": 2}))