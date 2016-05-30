"""
This module contains the WopMarsParsingException class
"""


class WopMarsParsingException(Exception):
    """
    WopMarsParsingException inheirt from Exception and is thrown during the "parsing-part" of the process.

    This exception is thrown with a context and a message. The context is supposed to explain where the exception has
    occured while the message gives more specific details about the exception.
    """
    # Those strings will be call byt the __str__ method depending on the context (which is the index of the string in
    # the tuple
    tpl_string_contexts = (
        "",
        "The YAML specification is not respected:",
        "The grammar of the WopMars's definition file is not respected:",
        "The ToolWrapper Input/Output specification is not respected:",
        "The ToolWrapper Option specification is not respected:",
        "The ToolWrapper has not been found:",
        "The specified Workflow cannot be represented as a DAG."
    )

    def __init__(self, context, message):
        """
        :param context: integer in range(5)
        :param message: string
        :return: void
        """
        assert context in range(len(WopMarsParsingException.tpl_string_contexts))
        self.__context = context
        self.__message = message

    def __str__(self):
        s = "Error while parsing the configuration file: \n\t"
        s += WopMarsParsingException.tpl_string_contexts[self.__context] + "\n\t\t"
        s += "\n\t\t".join(self.__message.split("\n"))
        return s
