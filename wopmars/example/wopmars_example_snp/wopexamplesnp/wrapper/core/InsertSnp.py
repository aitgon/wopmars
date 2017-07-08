from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

from sqlalchemy import select

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
        engine = session._WopMarsSession__session.bind
        conn = engine.connect()
        #
        snp_path = self.input_file(InsertSnp.__input_file_snp)
        snp_model = self.output_table(InsertSnp.__output_table_snp)
        #
        # RSIDs in table
        s = select([snp_model.rsid])
        rsid_in_db = {row[0]: None for row in conn.execute(s)}
        #
        # RSIDs in file
        new_snp_list = []
        keys = ['chrom', 'position', 'rsid']
        with open(snp_path, "r") as fin:
            for snp_line in fin.readlines():
                if snp_line.strip().split("\t")[2] not in rsid_in_db:
                    new_snp_obj_dic=dict(zip(keys, snp_line.strip().split("\t")))
                    new_snp_list.append(new_snp_obj_dic)
        #
        if not new_snp_list == []:
            engine.execute(snp_model.__table__.insert(), new_snp_list)

