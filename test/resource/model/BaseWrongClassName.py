from sqlalchemy import Column, Integer

from wopmars.framework.database.Base import Base


class Failure(Base):
    __tablename__ = "BaseWrongClassName"

    id = Column(Integer, primary_key=True, autoincrement=True)

