from wopmars.Base import Base

from wopmars.utils.WopMarsException import WopMarsException
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Option(Base):
    """
    The Option class handle a key and a value and is able to say if it is properly formated. It is also the model of the
    table ``wom_option`` which contains the following fields:

    - id: INTEGER - primary key - auto increment
    - is_input: VARCHAR(255) - the is_input of the referenced option
    - value: VRACHAR(255) - the value of the option
    - toolwrapper_id: INTEGER - the ID of the associated rule
    """

    # static value necessary to perform tests on Options
    static_option_castable = (
        "bool",
        "str",
        "int",
        "float"
       )
    static_option_req = "required"
    static_option_default = "optional"

    __tablename__ = "wom_{}".format(__qualname__)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    value = Column(String(255))
    toolwrapper_id = Column(Integer, ForeignKey("wom_ToolWrapper.id"))

    # One option is used by one rule
    relation_option_to_toolwrapper = relationship("ToolWrapper", back_populates="relation_toolwrapper_to_option",
                                                  enable_typechecks=False)

    def correspond(self, carac):
        """
        Check if the option value correspond to the type given by the tool wrapper. Throws a WopMarsException if
        not.

        :raise: WopMarsException
        :param carac: String containing the carac of the option in the format: "carac1|carac2|carc3"
        :return:
        """
        # get a list of caracteristics
        list_splitted_carac = carac.split("|")
        for s_type in list_splitted_carac:
            s_formated_type = s_type.strip().lower()
            # check if the carac is a autorized castable type
            if s_formated_type in Option.static_option_castable:
                try:
                    # try the cast
                    eval(s_formated_type)(self.value)
                except ValueError:
                    # if it fails, raise an exception: the type has not been respected
                    raise WopMarsException("The content of the definition file is not valid.",
                                           "The given option value of " + str(self.name) +
                                           " should be of type " + s_formated_type)

            # if not, it may be "default" or "required"
            else:
                # we check if an option is required and has no default value
                if s_formated_type != Option.static_option_default and s_formated_type != Option.static_option_req:
                    raise WopMarsException("Malformed tool_python_path class.",
                                           "The tool_python_path " + str(self.rule.toolwrapper) + " of the rule " +
                                           str(self.rule.name) + " has an incorrect \"specify_params\" method wich is " +
                                           "associating the " + self.name + " option with an unknown type. " +
                                           "Found: " + s_type + " - Allowed: " +
                                           str(",".join(Option.static_option_castable)))

    def __eq__(self, other):
        return self.value == other.value and self.name == other.name

    def __hash__(self):
        return id(self)

    def __str__(self):
        return str(self.name) + ": " + str(self.value)
