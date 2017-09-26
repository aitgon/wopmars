from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

import csv

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
        # read input file
        input_file_obj_list = []
        for line in csv.reader(open(snp2phenotype_path, 'r', encoding='utf-8'), delimiter="\t"):
            phenotype_name = line[1]
            input_file_obj = {'name': phenotype_name}
            input_file_obj_list.append(input_file_obj)
        #
        # insert input_file_obj_list
        if len(input_file_obj_list) > 0:
            if str(engine.__dict__['url']).split("://")[0]=='sqlite':
                engine.execute(phenotype_model.__table__.insert().prefix_with("OR IGNORE"), input_file_obj_list)
            elif str(engine.__dict__['url']).split("://")[0]=='mysql':
                    from warnings import filterwarnings # three lines to suppress mysql warnings
                    import MySQLdb as Database
                    filterwarnings('ignore', category = Database.Warning)
                    engine.execute(phenotype_model.__table__.insert().prefix_with("IGNORE"), input_file_obj_list)
            elif str(engine.__dict__['url']).split("://")[0]=='postgresql':
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                engine.execute(pg_insert(phenotype_model.__table__).on_conflict_do_nothing(index_elements=['name']), input_file_obj_list)
            else:
                raise "Error: This engine is not implemented."

