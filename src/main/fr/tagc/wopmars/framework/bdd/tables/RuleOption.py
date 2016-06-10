"""
Module containing the RuleOption class.
"""
from sqlalchemy import Column, Integer, ForeignKey

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class RuleOption(Base):
    __tablename__ = "rule_option"

    rule_id = Column(Integer, ForeignKey("rule.id"), primary_key=True)
    option_id = Column(Integer, ForeignKey("option.id"), primary_key=True)

    # Many to Many is automated by 'secondary' keywords in Rule and Option