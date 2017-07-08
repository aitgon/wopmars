from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP2Phenotype

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
        snp2phenotype_path = self.input_file(InsertSNP2Phenotype.__input_file_snp2phenotype)
        snp_model = self.input_table(InsertSNP2Phenotype.__input_table_snp)
        phenotype_model = self.input_table(InsertSNP2Phenotype.__input_table_phenotype)
        snp2phenotype_model = self.output_table(InsertSNP2Phenotype.__output_table_snp2phenotype)
        with open(snp2phenotype_path, "r") as fin:
            for snp2phenotype_line in fin.readlines():
                snp_id = None; phenotype_id = None
                # Query SNP id
                snp_rsid = snp2phenotype_line.strip().split("\t")[0]
                snp_dic= {'rsid': snp_rsid}
                try: # checks if exists Phenotype in db
                    snp_id = session.query(snp_model).filter_by(**snp_dic).one().id
                except: # if not, add
                    print("warning: SNP rsid not in db")
                # Query Phenotype id
                phenotype_name = snp2phenotype_line.strip().split("\t")[1]
                phenotype_dic= {'name': phenotype_name}
                try: # checks if exists Phenotype in db
                    phenotype_id = session.query(phenotype_model).filter_by(**phenotype_dic).one().id
                except: # if not, add
                    print("warning: Phenotype name not in db")
                if not snp_id is None and not phenotype_id is None:
                    # Insert SNP2Phenotype
                    snp2phenotype_dic = {'snp_id': snp_id, 'phenotype_id': phenotype_id}
                    try: # checks if exists Phenotype in db
                        session.query(snp2phenotype_model).filter_by(**snp2phenotype_dic).one()
                    except: # if not, add
                        snp2phenotype_instance = snp2phenotype_model(**snp2phenotype_dic)
                        session.add(snp2phenotype_instance)
                    session.commit()

