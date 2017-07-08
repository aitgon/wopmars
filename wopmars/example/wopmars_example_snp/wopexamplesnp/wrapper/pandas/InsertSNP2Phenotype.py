from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP2Phenotype

import pandas
from sqlalchemy import select

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
        #
        snp2phenotype_path = self.input_file(InsertSNP2Phenotype.__input_file_snp2phenotype)
        snp_model = self.input_table(InsertSNP2Phenotype.__input_table_snp)
        phenotype_model = self.input_table(InsertSNP2Phenotype.__input_table_phenotype)
        snp2phenotype_model = self.output_table(InsertSNP2Phenotype.__output_table_snp2phenotype)
        snp2phenotype_df = pandas.read_table(snp2phenotype_path, header=None)
        #
        # Get SNP table
        sql=select([snp_model.rsid, snp_model.id]).where(snp_model.rsid.in_(snp2phenotype_df[0].unique().tolist()))
        snp_df = session.pandas_read_sql(sql=sql, con=session._WopMarsSession__session.bind)
        snp_rsid2id_dic = dict(zip(snp_df['rsid'].tolist(), snp_df['id'].tolist()))
        #
        # Get Phenotype table
        sql=select([phenotype_model.name, phenotype_model.id]).where(phenotype_model.name.in_(snp2phenotype_df[1].unique().tolist()))
        phenotype_df = session.pandas_read_sql(sql=sql, con=session._WopMarsSession__session.bind)
        phenotype_name2id_dic = dict(zip(phenotype_df['name'].tolist(), phenotype_df['id'].tolist()))
        #
        # SNP2Phenotypes in table
        sql = select([snp2phenotype_model.snp_id, snp2phenotype_model.phenotype_id])
        snp2phenotype_in_db_df = session.pandas_read_sql(sql=sql, con=session._WopMarsSession__session.bind)
        #
        new_snp2phenotype_list = []
        for row in snp2phenotype_df.iterrows():
            snp_id = None
            phenotype_id = None
            if row[1][0] in snp_rsid2id_dic:
                snp_id = snp_rsid2id_dic[row[1][0]]
            if row[1][1] in phenotype_name2id_dic:
                phenotype_id = phenotype_name2id_dic[row[1][1]]
            if not snp_id is None and not phenotype_id is None:
                if not [snp_id, phenotype_id] in snp2phenotype_in_db_df.values.tolist():
                    new_snp2phenotype_list.append({'snp_id' : snp_id, 'phenotype_id' : phenotype_id})
        #
        df = pandas.DataFrame(new_snp2phenotype_list)
        session.pandas_to_sql(df, tablename=snp2phenotype_model.__dict__['__tablename__'], con=engine, if_exists='append', index=False)

