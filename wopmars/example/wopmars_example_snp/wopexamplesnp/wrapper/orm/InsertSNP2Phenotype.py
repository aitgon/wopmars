from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP2Phenotype

import csv

class InsertSNP2Phenotype(ToolWrapper): # inherit WopMars
    __mapper_args__ = {'polymorphic_identity': __name__}
    #
    __input_file_snp2phenotype = "snp2phenotype"
    __input_table_snp = "SNP"
    __input_table_phenotype = "Phenotype"
    __output_table_snp2phenotype = "SNP2Phenotype"

    def specify_input_file(self):
        return [InsertSNP2Phenotype.__input_file_snp2phenotype]

    def specify_input_table(self):
        return [InsertSNP2Phenotype.__input_table_snp,
                InsertSNP2Phenotype.__input_table_phenotype]

    def specify_output_table(self):
        return [InsertSNP2Phenotype.__output_table_snp2phenotype]

    def run(self):
        session = self.session()
        engine = session._WopMarsSession__session.bind
        conn = engine.connect()
        #
        snp2phenotype_path = self.input_file(InsertSNP2Phenotype.__input_file_snp2phenotype)
        snp_model = self.input_table(InsertSNP2Phenotype.__input_table_snp)
        phenotype_model = self.input_table(InsertSNP2Phenotype.__input_table_phenotype)
        snp2phenotype_model = self.output_table(InsertSNP2Phenotype.__output_table_snp2phenotype)
        #
        # read input file
        input_file_obj_list = []
        for line in csv.reader(open(snp2phenotype_path, 'r', encoding='utf-8'), delimiter="\t"):
            snp_rsid = int(line[0])
            phenotype_name = line[1]
            input_file_snp_obj = {'rsid': snp_rsid}
            input_file_phenotype_obj = {'name': phenotype_name}
            try: # checks if exists Phenotype in db
                snp_id = session.query(snp_model).filter_by(**input_file_snp_obj).one().id
                phenotype_id = session.query(phenotype_model).filter_by(**input_file_phenotype_obj).one().id
                input_file_obj = {'snp_id': snp_id, 'phenotype_id': phenotype_id}
                try: # checks if exists Phenotype in db
                    session.query(snp2phenotype_model).filter_by(**input_file_obj).one()
                except: # if not, add
                    snp2phenotype_instance = snp2phenotype_model(**input_file_obj)
                    session.add(snp2phenotype_instance)
                session.commit()
            except: # if not, add
                print("warning: SNP rsid or phenotype name not in db")

