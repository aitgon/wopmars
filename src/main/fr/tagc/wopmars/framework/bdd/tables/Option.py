"""
Module contianing the Option class
"""
from src.main.fr.tagc.wopmars.framework.bdd.Base import Base

from src.main.fr.tagc.wopmars.utils.OptionUtils import OptionUtils
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Option(Base):
    """
    The Option class handle a key and a value and is able to say if
    it is properly formated
    """

    __tablename__ = "wom_option"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(String)
    rule_id = Column(Integer, ForeignKey("wom_rule.id"))

    rule = relationship("ToolWrapper", back_populates="options", enable_typechecks=False)

    def correspond(self, carac):
        """
        Check if the option value correspond to the type given by the tool wrapper. Throws a WopMarsParsingException if
        not.

        :param carac: String containing the carac of the option in the format: "carac1|carac2|carc3"
        :return:
        """
        # get a list of caracs
        list_splitted_carac = carac.split("|")
        for s_type in list_splitted_carac:
            s_formated_type = s_type.strip().lower()
            # check if the carac is a castable type
            if s_formated_type in OptionUtils.static_option_castable:
                try:
                    # try the cast
                    eval(s_formated_type)(self.value)
                except ValueError:
                    # if it fails, raise an exception: the type has not been respected
                    raise WopMarsException(4, "The given option value of " + str(self.name) +
                                              " should be of type " + s_formated_type)
            else:
                # TODO exception de développeur métier qui a mal fait les choses
                pass

    def __eq__(self, other):
        return self.value == other.value and self.name == other.name

    def __hash__(self):
        return id(self)
