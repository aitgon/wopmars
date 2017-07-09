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
        #
        # read input file
        input_file_df=pandas.read_table(snp_path, header=None)
        input_file_df.columns=["chrom", "position", "rsid"] # rename columns
        input_file_dic_list=list(input_file_df.T.to_dict().values())
        #
        # read output db table
        sql = select([snp_model.chrom, snp_model.position, snp_model.rsid])
        output_table_df = session.pandas_read_sql(sql=sql, con=engine)
        output_table_dic_list=list(output_table_df.T.to_dict().values())
        #
        # prepare insert df - substract table df from file objs
        insert_dic_list=[i for i in input_file_dic_list if i not in output_table_dic_list]
        insert_df = pandas.DataFrame(insert_dic_list, columns=["chrom", "position", "rsid"]) # create insert df
        session.pandas_to_sql(insert_df, tablename=snp_model.__dict__['__tablename__'], con=engine, if_exists='append', index=False)

