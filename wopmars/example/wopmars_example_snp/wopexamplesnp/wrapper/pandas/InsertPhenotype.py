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
        # read input file
        input_file_df=pandas.read_table(snp2phenotype_path, header=None)
        input_file_df.columns=["id", "name"] # rename columns
        input_file_df=input_file_df[['name']].drop_duplicates()
        input_file_dic_list=list(input_file_df.T.to_dict().values())
        #
        # read output db table
        sql = select([phenotype_model.name])
        output_table_df = session.pandas_read_sql(sql=sql, con=engine)
        output_table_dic_list=list(output_table_df.T.to_dict().values())
        #
        # prepare insert df - substract table df from file objs
        insert_dic_list=[i for i in input_file_dic_list if i not in output_table_dic_list]
        insert_df = pandas.DataFrame(insert_dic_list, columns=['name']) # create insert df
        session.pandas_to_sql(insert_df, tablename=phenotype_model.__dict__['__tablename__'], con=engine, if_exists='append', index=False)

