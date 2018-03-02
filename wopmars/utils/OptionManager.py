"""
Module containing the OptionManager class.
"""
import os

from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.Singleton import SingletonMixin

from wopmars.constants import home_wopmars


class OptionManager(dict, SingletonMixin):
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
        self.validate_dir()
        self.validate_definition_file()
        self.validate_database()
        self.validate_dot()
        self.validate_log()
        self.validate_input_output_params()

        schema.validate(self)

        self.make_absolute_paths()

    def validate_input_output_params(self):
        if self["--input"] is None:
            self["--input"] = "{}"
        if self["--output"] is None:
            self["--output"] = "{}"
        if self["--params"] is None:
            self["--params"] = "{}"

    def validate_dir(self):
        if self["--directory"] == "$CWD":
            self["--directory"] = os.getcwd()

    def make_absolute_paths(self):
        if self["--wopfile"]:
            self["--wopfile"] = os.path.abspath(os.path.expanduser(self["--wopfile"]))
        if self["--log"]:
            self["--log"] = os.path.abspath(os.path.expanduser(self["--log"]))
        if self["--dot"]:
            self["--dot"] = os.path.abspath(os.path.expanduser(self["--dot"]))
        if self["--directory"]:
            self["--directory"] = os.path.abspath(os.path.expanduser(self["--directory"]))
        if self["--database"]:
            if self["--database"].split("://")[0]=="sqlite": # if sqlite replace with full path
                self["--database"]="sqlite:///" + os.path.abspath(os.path.expanduser(self["--database"].split(":///")[1]))
            # self["--database"] = {'db_connection': None, 'db_database': None, 'db_url': self["--database"]}
            # self["--database"]['db_connection'] = self["--database"]['db_url'].split("://")[0]
            # if self["--database"]['db_connection']=="sqlite":
            #     self["--database"]['db_database'] = os.path.abspath(os.path.expanduser(self["--database"]['db_url'].split(":///")[1]))

    def validate_definition_file(self):
        if self["--wopfile"] is None:
            self["--wopfile"] = "Wopfile"

    def validate_database(self):
        if self["--database"]:
            self["--database"] = os.path.expanduser(self["--database"])
        else:
            self["--database"] = os.path.join(self["--directory"], "sqlite:///db.sqlite")

    def validate_dot(self):
        if self["--dot"]:
            if self["--dot"][-1] == "/":
                self["--dot"] += "wopmars.dot"
            elif self["--dot"][-4:] != '.dot':
                self["--dot"] += ".dot"
            self["--dot"] = os.path.expanduser(self["--dot"])

    def validate_log(self):
        if self["--log"]:
            if self["--log"][0] == "$":
                self["--log"] = "~/.wopmars/wopmars.log"
            elif self["--log"][-1] == "/":
                self["--log"] += "wopmars.log"
            elif self["--log"][-4:] != '.log':
                self["--log"] += ".log"
            self["--log"] = os.path.expanduser(self["--log"])


    def __str__(self):
        s = ""

        s += "{\n\t"
        s += ",\n\t".join(["'" + str(k) + "': " + str(self[k]) for k in sorted(self.keys(), reverse=True)])
        s += "\n}"

        return s

    @staticmethod
    def initial_test_setup(mod_name="db"):
        if not os.path.isdir(home_wopmars):
            os.makedirs(home_wopmars)
        OptionManager.instance()["-v"] = 4
        OptionManager.instance()["--dot"] = None
        OptionManager.instance()["--log"] = os.path.join(os.path.expanduser("~"), ".wopmars/wopmars.log")
        OptionManager.instance()["--printtools"] = True
        OptionManager.instance()["--sourcerule"] = None
        OptionManager.instance()["--targetrule"] = None
        OptionManager.instance()["--forceall"] = None
        OptionManager.instance()["--dry-run"] = None
        OptionManager.instance()["tool"] = None
        OptionManager.instance()["--database"] = "sqlite:///" + os.path.join(PathFinder.get_module_path(), "test/output", mod_name + ".sqlite")
        OptionManager.instance()["--directory"] = PathFinder.get_module_path()
        OptionManager.instance()["--clear-history"] = False
        os.chdir(OptionManager.instance()["--directory"])
        OptionManager.instance()["--toolwrapper-log"] = False

