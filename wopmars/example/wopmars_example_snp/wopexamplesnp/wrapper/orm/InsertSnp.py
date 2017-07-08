from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

class InsertSnp(ToolWrapper): # inherit WopMars
    __mapper_args__ = {'polymorphic_identity': __name__}
    __input_file_snp = "snp"
    __output_table_snp = "SNP"

    def specify_input_file(self):
        return [InsertSnp.__input_file_snp]

    def specify_output_table(self):
        return [InsertSnp.__output_table_snp]

    def run(self):
        session = self.session()
        snp_path = self.input_file(InsertSnp.__input_file_snp)
        snp_model = self.output_table(InsertSnp.__output_table_snp)
        with open(snp_path, "r") as fin:
            keys = ['chrom', 'position', 'rsid']
            for snp_line in fin.readlines():
                snp_dic= dict(zip(keys, snp_line.strip().split("\t")))
                try: # checks if exists SNP in db
                    session.query(snp_model).filter_by(**snp_dic).one()
                except: # if not, add
                    snp_instance = snp_model(**snp_dic)
                    session.add(snp_instance)
                session.commit()


