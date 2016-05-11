"""
This module contains the DictUtils class.
"""


class DictUtils:
    """
    Class containing methods that are usefull for dealing with dicts
    """
    # TODO: tesunitaire sur cette classe
    @staticmethod
    def all_elm_of_one_dict_in_one_other(one, other):
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


if __name__ == "__main__":
    print(DictUtils.all_elm_of_one_dict_in_one_other({"a": 1}, {"a": 1, "b": 2}))