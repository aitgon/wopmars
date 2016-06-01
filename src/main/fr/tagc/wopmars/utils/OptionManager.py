"""
Module containing the OptionManager class.
"""
from fr.tagc.wopmars.utils.Singleton import singleton



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
        schema.validate(self)

    def __str__(self):
        s = ""

        s += "{\n\t"
        s += ",\n\t".join(["'" + str(k) + "': " + str(self[k]) for k in sorted(self.keys(), reverse=True)])
        s += "\n}"

        return s
