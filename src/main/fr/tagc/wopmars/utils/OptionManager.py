"""
Module containing the OptionManager class.
"""
from src.main.fr.tagc.wopmars.utils.Singleton import singleton


@singleton
class OptionManager(dict):
    """
    The OptionManager contains the command-line argument and can be retrieved from whereever in the software.

    OptionManager inherit from dict so it behaves exactly the same but takes only one possible argument.
    """

    def __init__(self, *args, **kwargs):
        """
        :param: dict_args: dictionnary containing the arguments passed to the command line.
        :return: void
        """
        super().__init__(*args, **kwargs)

    def validate(self, schema):
        self.validate_dot()
        self.validate_log()

        schema.validate(self)

    def validate_dot(self):
        if self["--dot"]:
            if self["--dot"][-1] == "/":
                self["--dot"] += "wopmars.dot"
            elif self["--dot"][-4:] != '.dot':
                self["--dot"] += ".dot"

    def validate_log(self):
        if self["--log"]:
            if self["--log"][-1] == "/":
                self["--log"] += "wopmars.log"
            elif self["--log"][-4:] != '.log':
                self["--log"] += ".log"

    def __str__(self):
        s = ""

        s += "{\n\t"
        s += ",\n\t".join(["'" + str(k) + "': " + str(self[k]) for k in sorted(self.keys(), reverse=True)])
        s += "\n}"

        return s
