from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

from sqlalchemy import select

class InsertPhenotype(ToolWrapper): # inherit WopMars
    __mapper_args__ = {'polymorphic_identity': __name__}
    __input_file_snp2phenotype = "snp2phenotype"
    __output_table_phenotype = "Phenotype"

    def specify_input_file(self):
        return [InsertPhenotype.__input_file_snp2phenotype]

    def specify_output_table(self):
        return [InsertPhenotype.__output_table_phenotype]

    def run(self):
        session = self.session()
        engine = session._WopMarsSession__session.bind
        conn = engine.connect()
        #
        snp2phenotype_path = self.input_file(InsertPhenotype.__input_file_snp2phenotype)
        phenotype_model = self.output_table(InsertPhenotype.__output_table_phenotype)
        #
        # Phenotypes in table
        s = select([phenotype_model.name])
        phenotype_in_db = {row[0]: None for row in conn.execute(s)}
        #
        # Phenotypes in file
        new_phenotype_list = []
        with open(snp2phenotype_path, "r") as fin:
            keys = ['name']
            for snp2phenotype_line in fin.readlines():
                phenotype_name = snp2phenotype_line.strip().split("\t")[1]
                if not phenotype_name in phenotype_in_db:
                    phenotype_dic= {'name': phenotype_name}
                    if not phenotype_dic in new_phenotype_list:
                        new_phenotype_list.append(phenotype_dic)
        #
        if not new_phenotype_list == []:
            engine.execute(phenotype_model.__table__.insert(), new_phenotype_list)

