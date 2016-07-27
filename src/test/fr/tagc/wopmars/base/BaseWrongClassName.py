from sqlalchemy import Column, Integer

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base


class Failure(Base):
    __tablename__ = "BaseWrongClassName"

    id = Column(Integer, primary_key=True, autoincrement=True)

