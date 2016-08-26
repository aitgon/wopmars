"""
This module contains the WopMarsException class
"""


class WopMarsException(Exception):
    """
    WopMarsException inherit from Exception and is thrown by every part of the .

    This exception is thrown with a context and a message. The context is supposed to explain where the exception has
    occured while the message gives more specific details about the exception.
    """

    def __init__(self, context="", message=""):
        """
        :param context: String that contains the context
        :param message: string that contains the precise error
        :return: void
        """
        self.__context = context
        self.__message = message

    def __str__(self):
        s = ""
        if self.__context:
            s += self.__context + "\n\t\t"
        if self.__message:
            s += "\n\t\t".join(self.__message.split("\n"))
        return s
