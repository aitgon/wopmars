"""
This module contains the ToolWrapper class
"""


from src.main.fr.tagc.wopmars.utils.DictUtils import DictUtils
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException
from src.main.fr.tagc.wopmars.framework.management.Observable import Observable


class ToolWrapper(Observable):
    """
    The class ToolWrapper is the superclass of the Wrapper which
    will be designed by the wrapper developers.
    """

    NEW = 1
    READY = 2
    NOT_READY = 3

    def __init__(self, input_file_dict={}, output_file_dict={}, option_dict={}):
        """
        The constructor of the toolwrapper, must not be overwritten.

        set_observer is the set of all observers of the toolwrappers.
        input_file_dict is the dict containing the IOFilePut objects of the file input of the toolwrapper.
        option_dict is the dict containing the Option objects of the params of the toolwrapper.
        output_file_dict is the dict containing the IOFilePut objects of the file output of the toolwrapper.
        state is the constant refering to the state of the toolwrapper, it is initialized at "NEW"

        :param input_file_dict: dict(String: IOPUT)
        :param output_file_dict: dict(String: IOPUT)
        :param option_dict: dict(String: Option)
        :return: void
        """
        assert type(input_file_dict) == dict and type(output_file_dict) == dict and type(option_dict) == dict
        # self.__set_observer = set([])
        self.__input_file_dict = input_file_dict
        self.__output_file_dict = output_file_dict
        self.__option_dict = option_dict
        self.__state = ToolWrapper.NEW
        self.__session = None

    def is_content_respected(self):
        """
        This method checks if the parameters dictionary are properly formed, according to the specifications of the
        wrapper developer.

        :return:
        """

        # the options have to be checked first because they can alter the behavior of the is_input_respected and
        # is_output_respected methods
        self.is_options_respected()

        self.is_input_respected()
        self.is_output_respected()

    def is_input_respected(self):
        """
        Check if the input dictionary given in the constructor is properly formed for the tool.

        It checks if the output variable names exists or not.
        If not, throws a WopMarsParsingException(3)
        :return:void
        """
        if set(self.__input_file_dict.keys()) != set(self.get_input_file()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given input variable's names for " + self.__class__.__name__ +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.get_input_file())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(self.__input_file_dict.keys()))
                                   )

    def is_output_respected(self):
        """
        Check if the output dictionary given in the constructor is properly formed for the tool.

        It checks if the output variable names exists or not. Throws WopMarsParsingException if not
        :return:void
        """
        if set(self.__output_file_dict.keys()) != set(self.get_output_file()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given output variable names for " + self.__class__.__name__ +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.get_output_file())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(self.__output_file_dict.keys()))
                                   )

    def is_options_respected(self):
        """
        This method check if the params given in the constructor are properly formed for the tool.

        It checks if the params names given by the user exists or not, if the type correspond and if the required
        options are given
        :return:
        """
        dict_wrapper_opt_carac = self.get_params()

        # check if the given options are authorized
        if not set(self.__option_dict.keys()).issubset(dict_wrapper_opt_carac):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given option variable for " + self.__class__.__name__ +
                                   " are not correct, they should be in: " +
                                   "\n\t'{0}'".format("'\n\t'".join(dict_wrapper_opt_carac)) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(self.__option_dict.keys()))
                                   )

        # check if the types correspond
        for opt in self.__option_dict:
            self.__option_dict[opt].correspond(dict_wrapper_opt_carac[opt])

        # check if the required options are given
        for opt in dict_wrapper_opt_carac:
            if "required" in dict_wrapper_opt_carac[opt].lower() and opt not in self.__option_dict.keys():
                raise WopMarsException("The content of the definition file is not valid.",
                                       "The option " + opt + " has not been provided but it is required.")

    def follows(self, other):
        """
        Check whether the "other" follows "self" in the execution DAG.

        Check whether "other" has one output value in "self" possible input values.
        :param other: ToolWrapper that is possibly a predecessor of "self"
        :return: bool True if "self" follows "other"
        """
        return DictUtils.at_least_one_value_of_one_in_an_other(self.__input_file_dict, other.get_output_file_dict())

# todo enlever commentaires
    # def start(self):
    #     """
    #     Run the tool and fire events.
    #     :return:
    #     """
    #     Logger().info(self.__class__.__name__ + " started.")
    #     self.run()
    #     self.fire_success()

    # def get_observers(self):
    #     """
    #     Return the set of observers.
    #
    #     :return: set observers
    #     """
    #     return self.__set_observer
    #
    # def subscribe(self, obs):
    #     """
    #     An observer subscribes to the obervable.
    #
    #     :param obs:
    #     :return:
    #     """
    #     self.__set_observer.add(obs)
    #
    # def fire_failure(self):
    #     """
    #     Notify all ToolWrapperObservers that the execution has failed.
    #
    #     :return:
    #     """
    #     for obs in self.get_observers():
    #         obs.notify_failure(self)
    #
    # def fire_success(self):
    #     """
    #     Notify all ToolWrapperObservers that the run has suceeded
    #
    #     :return:
    #     """
    #     for obs in self.get_observers():
    #         obs.notify_success(self)

    def are_inputs_ready(self):
        """
        Check if inputs are ready

        :return: bool - True if inputs are ready.
        """
        Logger().debug("Inputs of " + str(self.__class__.__name__) + ": " + str(self.__input_file_dict.keys()))
        for input_name in self.__input_file_dict:
            if not self.__input_file_dict[input_name].is_ready():
                Logger().debug("Input: " + str(input_name) + " is not ready.")
                self.__state = ToolWrapper.NOT_READY
                return False
            Logger().debug("Input: " + str(input_name) + " is ready.")
        self.__state = ToolWrapper.READY
        return True

    def get_state(self):
        return self.__state

    def set_session(self, session):
        self.__session = session

    def __eq__(self, other):
        """
        Two ToolWrapper objects are equals if their attributes are equals
        :param other: ToolWrapper
        :return:
        """

        return (
                isinstance(other, self.__class__) and
                DictUtils.elm_of_one_dict_in_one_other(self.__input_file_dict, other.get_input_file_dict()) and
                DictUtils.elm_of_one_dict_in_one_other(self.__output_file_dict, other.get_output_file_dict()) and
                DictUtils.elm_of_one_dict_in_one_other(self.__option_dict, other.get_option_dict())
        )

    def __hash__(self):
        """
        Redefining the hash method allows ToolWrapper objects to be indexed in sets and dict
        :return:
        """
        return id(self)

    def __repr__(self):
        """
        Return the string representing the toolwrapper in the DAG.

        :return: String representing the toolwrapper
        """
        s = "\""
        s += self.__class__.__name__
        s += "\\n"
        for key in self.__input_file_dict:
            s += "\\n\t\t" + key + ": " + str(self.__input_file_dict[key])
        s += "\\n"
        for key in self.__output_file_dict:
            s += "\\n\t\t" + key + ": " + str(self.__output_file_dict[key])
        s += "\""
        return s

    # ###### Method relatives to the framework #######

    def get_input_file_dict(self):
        return self.__input_file_dict

    def get_output_file_dict(self):
        return self.__output_file_dict

    def get_option_dict(self):
        return self.__option_dict

    def create_base_object_from_name(self):
        # TODO this method will return (or set self attributes) from class names to base. Il n'y a peut etre pas besoin
        # que cette méthode soit dans self
        pass

    def get_input_file(self):
        return []

    def get_input_db(self):
        return []

    def get_output_file(self):
        return []

    def get_output_db(self):
        return []

    def get_params(self):
        return {}

    def run(self):
        pass

    def input(self, key):
        return self.__input_file_dict[key].get_path()

    def output(self, key):
        return self.__output_file_dict[key].get_path()

    def option(self, key):
        return self.__option_dict[key].get_value()

    def session(self):
        return self.__session