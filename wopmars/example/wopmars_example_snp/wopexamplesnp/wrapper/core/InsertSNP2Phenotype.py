from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP2Phenotype

import pandas
from sqlalchemy import select,insert
from sqlalchemy.sql.expression import bindparam
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
        snp2phenotype_df = pandas.read_table(snp2phenotype_path, header=None)
        #
        # read input file
        input_file_obj_list = []
        for line in csv.reader(open(snp2phenotype_path, 'r', encoding='utf-8'), delimiter="\t"):
            snp_rsid = int(line[0])
            phenotype_name = line[1]
            input_file_obj_list.append({'snp_rsid' : snp_rsid, 'phenotype_name' : phenotype_name})
        #
        # create insert
        snp_select = select([snp_model.id]).where(snp_model.rsid==bindparam('snp_rsid'))
        phenotype_select = select([phenotype_model.id]).where(phenotype_model.name==bindparam('phenotype_name'))
        output_table_insert = insert(table=snp2phenotype_model.__table__, values={'snp_id': snp_select, 'phenotype_id': phenotype_select})
        #
        if len(input_file_obj_list) > 0:
            if str(engine.__dict__['url']).split("://")[0]=='sqlite':
                engine.execute(output_table_insert.prefix_with("OR IGNORE", dialect='sqlite'), input_file_obj_list)
            elif str(engine.__dict__['url']).split("://")[0]=='mysql':
                    from warnings import filterwarnings # three lines to suppress mysql warnings
                    import MySQLdb as Database
                    filterwarnings('ignore', category = Database.Warning)
                    engine.execute(output_table_insert.prefix_with("IGNORE", dialect='mysql'), input_file_obj_list)
            elif str(engine.__dict__['url']).split("://")[0]=='postgresql':
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                output_table_insert_pg = pg_insert(table=snp2phenotype_model.__table__, values={'snp_id': snp_select, 'phenotype_id': phenotype_select}).on_conflict_do_nothing(index_elements=['snp_id', 'phenotype_id'])
                engine.execute(output_table_insert_pg, input_file_obj_list)

