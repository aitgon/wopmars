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
        # read input file
        input_file_df=pandas.read_table(snp2phenotype_path, header=None)
        input_file_df.columns=["snp_rsid", "phenotype_name"] # rename columns
        input_file_dic_list=list(input_file_df.T.to_dict().values())
        #
        # rsid2id_dic
        sql=select([snp_model.rsid, snp_model.id]).where(snp_model.rsid.in_(snp2phenotype_df[0].unique().tolist()))
        snp_df = session.pandas_read_sql(sql=sql, con=session._WopMarsSession__session.bind)
        snp_rsid2id_dic = dict(zip(snp_df['rsid'].tolist(), snp_df['id'].tolist()))
        #
        # phenotype_name2id_dic
        sql=select([phenotype_model.name, phenotype_model.id]).where(phenotype_model.name.in_(snp2phenotype_df[1].unique().tolist()))
        phenotype_df = session.pandas_read_sql(sql=sql, con=session._WopMarsSession__session.bind)
        phenotype_name2id_dic = dict(zip(phenotype_df['name'].tolist(), phenotype_df['id'].tolist()))
        #
        # read output SNP2Phenotype table
        sql = select([snp2phenotype_model.snp_id, snp2phenotype_model.phenotype_id])
        output_table_df = session.pandas_read_sql(sql=sql, con=engine)
        output_table_dic_list=list(output_table_df.T.to_dict().values())
        #
        # create insert_dic_list based on ids, and not already present in table
        insert_dic_list = []
        for item in input_file_dic_list:
            snp_rsid = item['snp_rsid']
            phenotype_name = item['phenotype_name']
            snp_id = None
            phenotype_id = None
            if snp_rsid in snp_rsid2id_dic:
                snp_id = snp_rsid2id_dic[snp_rsid]
            if phenotype_name in phenotype_name2id_dic:
                phenotype_id = phenotype_name2id_dic[phenotype_name]
            if not snp_id is None and not phenotype_id is None:
                if not {'snp_id': snp_id, 'phenotype_id': phenotype_id} in output_table_dic_list:
                    insert_dic_list.append({'snp_id' : snp_id, 'phenotype_id' : phenotype_id})
        #
        insert_df = pandas.DataFrame(insert_dic_list, columns=['snp_id', 'phenotype_id'])
        session.pandas_to_sql(insert_df, tablename=snp2phenotype_model.__dict__['__tablename__'], con=engine, if_exists='append', index=False)

