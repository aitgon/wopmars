from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.Phenotype

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
        snp2phenotype_path = self.input_file(InsertPhenotype.__input_file_snp2phenotype)
        phenotype_model = self.output_table(InsertPhenotype.__output_table_phenotype)
        with open(snp2phenotype_path, "r") as fin:
            keys = ['name']
            for snp2phenotype_line in fin.readlines():
                phenotype_name = snp2phenotype_line.strip().split("\t")[1]
                phenotype_dic= {'name': phenotype_name}
                try: # checks if exists Phenotype in db
                    session.query(phenotype_model).filter_by(**phenotype_dic).one()
                except: # if not, add
                    phenotype_instance = phenotype_model(**phenotype_dic)
                    session.add(phenotype_instance)
                session.commit()


