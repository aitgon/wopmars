# import pandas

from wopmars.main.tagc.framework.bdd.tables.ToolWrapper import ToolWrapper # required import

# def get_or_create(session, model, **kwargs):
#     try:
#         return session.query(model).filter_by(**kwargs).one(), False
#     except NoResultFound:
#         instance = model(**kwargs)
#         session.add(instance)
#         session.commit()
#         return instance, True

class SparePartsManufacturer(ToolWrapper): # required class definition
    __mapper_args__ = {'polymorphic_identity': __name__} # required line
    # my I/O vars
    __input_file_piece = "piece"
    __output_table_piece = "Piece"

    def specify_input_file(self):
        # defines input piece file field in previous workflow definition
        return [SparePartsManufacturer.__input_file_piece]

    def specify_output_table(self):
        # defines output piece table field in previous workflow definition
        return [SparePartsManufacturer.__output_table_piece]

    def run(self):
        session = self.session() # inherit session
        piece_path = self.input_file(SparePartsManufacturer.__input_file_piece) # string
        piece_m = self.output_table(SparePartsManufacturer.__output_table_piece) # model class
        with open(piece_path, "r") as fin:
            for line_str in fin.readlines():
                line_str = line_str.strip()
                line_list = line_str.split("\t")
                serial_number = line_list[0]
                typee = line_list[1]
                price = line_list[2]
                try: # check if exists
                    session.query(piece_m).filter_by(serial_number=serial_number, type2=typee, price=price).one()
                except: # if not commit
                    instance = piece_m(serial_number=serial_number, type2=typee, price=price)
                    session.add(instance)
                session.commit()

