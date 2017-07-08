from wopmars.framework.database.tables.ToolWrapper import ToolWrapper

# import models
import wopexamplesnp.model.SNP

import pandas
from sqlalchemy import select

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
        #
        snp2phenotype_path = self.input_file(InsertPhenotype.__input_file_snp2phenotype)
        phenotype_model = self.output_table(InsertPhenotype.__output_table_phenotype)
        #
        # read file phenotypes
        df=pandas.read_table(snp2phenotype_path, header=None)
        df.columns=["id", "name"] # rename columns
        df = pandas.DataFrame(data=df.ix[:,'name']).drop_duplicates()
        #
        # read db phenotypes
        sql = select([phenotype_model.name])
        df_in_db = session.pandas_read_sql(sql=sql, con=engine)
        df = df[~df.name.isin(df_in_db.name)] # substract objects in db
        session.pandas_to_sql(df, tablename=phenotype_model.__dict__['__tablename__'], con=engine, if_exists='append', index=False)

