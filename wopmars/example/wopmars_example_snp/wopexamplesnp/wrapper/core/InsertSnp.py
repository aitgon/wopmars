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
        engine = session._WopMarsSession__session.bind
        conn = engine.connect()
        #
        snp_path = self.input_file(InsertSnp.__input_file_snp)
        snp_model = self.output_table(InsertSnp.__output_table_snp)
        #
        # read input file
        input_file_obj_list = []
        for line in csv.reader(open(snp_path, 'r', encoding='utf-8'), delimiter="\t"):
            chrom = int(line[0])
            position = int(line[1])
            rsid = int(line[2])
            input_file_obj = {'chrom': chrom, 'position': position, 'rsid': rsid}
            input_file_obj_list.append(input_file_obj)
        #
        # insert input_file_obj_list
        if len(input_file_obj_list) > 0:
            if str(engine.__dict__['url']).split("://")[0]=='sqlite':
                engine.execute(snp_model.__table__.insert().prefix_with("OR IGNORE"), input_file_obj_list)
            elif str(engine.__dict__['url']).split("://")[0]=='mysql':
                    from warnings import filterwarnings # three lines to suppress mysql warnings
                    import MySQLdb as Database
                    filterwarnings('ignore', category = Database.Warning)
                    engine.execute(snp_model.__table__.insert().prefix_with("IGNORE"), input_file_obj_list)
            elif str(engine.__dict__['url']).split("://")[0]=='postgresql':
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                engine.execute(pg_insert(snp_model.__table__).on_conflict_do_nothing(index_elements=['rsid']), input_file_obj_list)
            else:
                raise "Error: This engine is not implemented."

