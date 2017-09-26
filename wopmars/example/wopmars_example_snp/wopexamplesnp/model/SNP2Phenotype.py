from wopmars.framework.database.Base import Base

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy import UniqueConstraint

class SNP2Phenotype(Base):
    __tablename__ = 'SNP2Phenotype'
    __table_args__ = (
            UniqueConstraint('snp_id', 'phenotype_id'),
            )

    id = Column(Integer, primary_key=True, autoincrement=True)
    snp_id = Column(Integer, ForeignKey("SNP.id"), nullable=False)
    phenotype_id = Column(Integer, ForeignKey("Phenotype.id"), nullable=False)

