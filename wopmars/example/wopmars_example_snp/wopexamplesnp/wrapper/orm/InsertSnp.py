from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

import csv

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
        #
        snp_path = self.input_file(InsertSnp.__input_file_snp)
        snp_model = self.output_table(InsertSnp.__output_table_snp)
        #
        # read input file
        input_file_dic_list = []
        for line in csv.reader(open(snp_path, 'r', encoding='utf-8'), delimiter="\t"):
            chrom = line[0]
            position = line[1]
            rsid = line[2]
            input_file_obj = {'chrom': chrom, 'position': position, 'rsid': rsid}
            try: # checks if exists SNP in db
                session.query(snp_model).filter_by(**input_file_obj).one()
            except: # if not, add
                session.add(snp_model(**input_file_obj))
            session.commit()


