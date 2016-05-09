"""
Module containing the IOPut class
"""


class IOPut:
    """
    This class will never be instantiated, it will be extended.
    """    
    def __init__(self, name):
        """
        :param name: String: the name of the variable containing
        the IOPut in the definition file

        :return: void
        """
        self.__name = name

    def is_ready(self):
        """
        Check if the resource contained by self exists on the hard drive.
        This method will be written in subclasses
        :return: boolean: True if ready, False if not
        """
        pass

    def get_name(self):
        """
        Return the name of the IOPut

        :return: String: the name
        """
        return self.__name
