The Models
-----------------

.. note::

    A data model is an abstract representation of data. In the field of the OOP and the work with a relational database, we can consider a model like a class which represent a data type in the database (usually a row in a table). The model have to describe the types of each field and their relations with the other tables (meanning other models).
    
For the rest of this section, I assume that you have iterate_wopfile_yml_dic_and_insert_rules_in_db and understood the secion `"Declare a Mapping" <http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#declare-a-mapping>`_ of the SQLAlchemy tutorial.

A model have to be associated with a database. This is why the models used in WopMars have to inherit from the class ``Base``. ``Base`` is a class which will be associated itself with a SQLite database (a file) and which contains every information related: the tables, the relations, etc..

To declare a model, even before specifying fiels, it is necessary that you give a name to the table thanks to the static attribute ``__tablename__``. the content of this variable is extremely important because this is the name which will be returned by the methods ``specify_input_table`` and ``specify_output_table`` of your `Toolwrappers` and which will be used by the final user to referencing the table in the definition file.

Most of the functionnalities described in the SQLAlchemy tutorial are also available in WopMars models, especially the foreign key and relationship system between models. If ever, you find a missing functionnality, do not hesitate and send us an issue. This is also important to notive that the foreign key constraints have been enforced for WopMars, meaning that if you do not respect those constraints in your `Toolwrapper`, you'll get an error.

