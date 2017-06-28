"""
This module contains the SetUtils class.
"""


class SetUtils:
    """
    Class containing methods that are usefull for dealing with sets
    """
    @staticmethod
    def all_elm_of_one_set_in_one_other(one, other):
        """
        Check if all elements of one set is in an other. The build in functions cannot be used (set.issubset()) because
        they rely on the hash of elements and not on their values.

        :param one: set
        :param other: set
        :return: boolean: True if all elements of one are in the other
        """
        for elm in one:
            is_in = False
            for elm2 in other:
                if elm == elm2:
                    is_in = True
                    break # Useless to keep looking in the other set since we just want to see if elm occurs once
            if not is_in:
                return False
        return True

