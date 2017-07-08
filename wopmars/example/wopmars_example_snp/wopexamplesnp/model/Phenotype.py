from wopmars.framework.database.Base import Base

from sqlalchemy import Column, String, Integer
from sqlalchemy import UniqueConstraint

class Phenotype(Base):
    __tablename__ = 'Phenotype'
    __table_args__ = (
            )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

