from wopmars.Base import Base

from sqlalchemy import Column, String, Integer


class Phenotype(Base):
    __tablename__ = 'Phenotype'
    __table_args__ = (
            )

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

