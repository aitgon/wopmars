"""
Module containing the IOFilePut class
"""
import os

from fr.tagc.wopmars.framework.rule.IOPut import IOPut


class IOFilePut(IOPut):
    """
    This class extends IOPut and is specific to file input or output
    """
    def __init__(self, name, path):
        """
        :param name: String: the name of the variable in the
        workflow definition file
        :param oath: String: the path leading to the actual file
        on the hard drive
        :return: void
        """
        super().__init__(name)
        self.__path = path

    def get_path(self):
        """
        Return the path to the file on the hard drive

        :return: String: the path
        """
        return self.__path

    def is_ready(self):
        """
        Check if the file exists on the hard drive

        :return: boolean: True if it exists, false if not
        """
        return os.path.isfile(self.__path)

    def __eq__(self, other):
        return self.__path == other.get_path()

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "file:'" + self.__path + "'"
