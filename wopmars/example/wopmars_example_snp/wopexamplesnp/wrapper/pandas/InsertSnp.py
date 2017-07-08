from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

import pandas
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
        #
        snp_path = self.input_file(InsertSnp.__input_file_snp)
        snp_model = self.output_table(InsertSnp.__output_table_snp)
        # read file snps
        df=pandas.read_table(snp_path, header=None)
        df.columns=["chrom", "position", "rsid"] # rename columns
        df['key']=df['chrom']+df['position'].astype(str)+df['rsid'] # create key
        #
        # read db snps
        sql = select([snp_model.chrom, snp_model.position, snp_model.rsid])
        df_in_db = session.pandas_read_sql(sql=sql, con=engine)
        df_in_db['key'] = df_in_db['chrom']+df_in_db['position'].astype(str)+df_in_db['rsid']
        df = df[~df.key.isin(df_in_db.key)] # substract objects in db
        df.drop('key', axis=1, inplace=True)
        session.pandas_to_sql(df, tablename=snp_model.__dict__['__tablename__'], con=engine, if_exists='append', index=False)
        