"""
Module containing the Rule class.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Rule(Base):
    __tablename__ = "rule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    toolwrapper_id = Column(Integer, ForeignKey("toolwrapper.id"), nullable=False)

    # One rule has One toolwrapper
    toolwrapper = relationship("ToolWrapper", back_populates="rules")

    # One rule is in Many rule_table and has Many table
    tables = relationship("RuleTable", back_populates="rule")
    # One rule is in Many rule_file and has Many file
    files = relationship("RuleFile", back_populates="rule")
    # One rule has Many option
    options = relationship("Option", secondary="rule_option", back_populates="rules")

    childrules = relationship("Rule",
                              secondary="rule_rule",
                              primaryjoin="Rule.id==rule_rule.c.rule_parent_id",
                              secondaryjoin="Rule.id==rule_rule.c.rule_child_id",
                              backref="parentrules")

    def __repr__(self):
        return "<Rule (name='%s', toolwrapper_id='%s')>" % (self.name, self.toolwrapper_id)
