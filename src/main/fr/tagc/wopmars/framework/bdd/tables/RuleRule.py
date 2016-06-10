"""
Module containing the RuleRule class.
"""
from sqlalchemy import Column, Integer,  ForeignKey

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class RuleRule(Base):
    __tablename__ = "rule_rule"

    rule_parent_id = Column(Integer, ForeignKey("rule.id"), primary_key=True)
    rule_child_id = Column(Integer, ForeignKey("rule.id"), primary_key=True)
