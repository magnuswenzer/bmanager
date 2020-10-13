import sqlite3
from sqlite3 import Error
from bmanager.database import Database
from bmanager import utils, exceptions
import datetime
from pathlib import Path


class SqliteDatabase(Database):

    def __init__(self, location=None):
        self.location = location
        print('$'*100)
        print('$'*100)
        print(f'Database location is: {Path(self.location).absolute()}')
        print('$'*100)
        print('$'*100)

    def _execute(self, sql_command, variables=None, commit=False, fetchall=False):
        """
        Execute the given sql command.
        """
        conn = None
        result = True

        print('='*30)
        print('SQL COMMAND')
        print('-'*30)
        print(sql_command)
        print('-'*30)
        print('variables', variables)

        try:
            conn = sqlite3.connect(self.location)
            c = conn.cursor()

            if variables:
                c.execute(sql_command, variables)
            else:
                c.execute(sql_command)

            if fetchall:
                result = c.fetchall()

            if commit or fetchall or variables:
                conn.commit()

        except Error as e:
            print('+'*50)
            print(e)
            print('+'*50)
            if 'UNIQUE' in str(e):
                raise exceptions.AlreadyInDatabase(e)
            else:
                raise exceptions.BmanagerException(e)
        finally:
            if conn:
                conn.close()

        return result

    def create_database(self):
        """
        Creates the database by simply connecting to it.
        """
        print(f'Creating the database at: {self.location}')
        conn = None
        try:
            conn = sqlite3.connect(self.location)
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()

    def create_tables(self, table_list):
        for table in table_list:
            self._create_table(table)
            self._update_table(table)

    def _create_table(self, table_info):
        sql = f"""CREATE TABLE IF NOT EXISTS {table_info.get('name')} (\n"""
        columns = []
        unique_combo = []
        for col in table_info.get('columns'):
            if col.get('not_in_db'):
                continue
            string = f"""{col.get('name')} {col.get('data_type')}"""
            if col.get('primary_key'):
                string = string + ' PRIMARY KEY'
            elif col.get('mandatory'):
                string = string + ' NOT NULL'
                if col.get('unique'):
                    string = string + ' UNIQUE'
            if col.get('unique_combo'):
                unique_combo.append(col.get('name'))
            columns.append(string)
        if unique_combo:
            unique_combo_str = f"UNIQUE({', '.join(unique_combo)})"
            columns.append(unique_combo_str)
        sql = sql + ',\n'.join(columns) + '\n);'
        self._execute(sql)

    def _update_table(self, table_info):
        current_columns = self.get_columns_in_table(table_info.get('name'))
        for col in table_info.get('columns'):
            if col.get('name') in current_columns:
                continue
            if col.get('not_in_db'):
                continue
            sql = f"""ALTER TABLE {table_info.get('name')} ADD COLUMN {col.get('name')} {col.get('data_type')}"""
            self._execute(sql)

    def get_columns_in_table(self, table):
        conn = None
        result = False
        try:
            conn = sqlite3.connect(self.location)
            cursor = conn.execute(f"""SELECT * FROM {table}""")
            result = [des[0] for des in cursor.description]
        except Error as e:
            raise
        finally:
            if conn:
                conn.close()

        return result

    def add_to_table(self, table, **kwargs):
        columns = self.get_columns_in_table(table)
        if 'id' in columns:
            columns.pop(columns.index('id'))
        values = []
        for col in columns:
            if col == 'time':
                values.append(datetime.datetime.now())
            else:
                values.append(kwargs.get(col, ''))

        sql_insert = f"""
                      INSERT INTO {table} ({', '.join(columns)}) 
                      VALUES ({', '.join(['?']*len(columns))})
                      """
        return self._execute(sql_insert, variables=values)

    def get_from_table(self, table, columns=[], **kwargs):

        # Check dates
        datetime_synonyms = utils.get_datetime_synonyms()

        sql_select = f"""SELECT {column_string(columns)} FROM {table_string(table)} {where_string(**kwargs)}"""
        result = self._execute(sql_select, fetchall=True)
        return_list = []
        for row in result:
            if columns:
                row_dict = dict(zip(columns, row))
            else:
                row_dict = dict(zip(self.get_columns_in_table(table), row))
                # TODO: All columns should be based on config instead of table columns?
            for key, value in row_dict.items():
                if not value:
                    continue
                if key in datetime_synonyms:
                    value = utils.get_datetime_from_string(value)
                    row_dict[key] = value
            return_list.append(row_dict)
        return return_list

    def get_query(self, query):
        return self._execute(query, fetchall=True)

    def update_table(self, table, data, **kwargs):
        variables = []
        set_list = []
        for key, value in data.items():
            variables.append(value)
            set_list.append(f"""{key} = ?""")
        set_str = f"""SET {', '.join(set_list)}"""
        update_sql = f""" UPDATE {table} {set_str} {where_string(**kwargs)}"""
        self._execute(update_sql, variables=variables)


def table_string(table):
    if type(table) == list:
        return ', '.join(table)
    return table


def column_string(columns=[]):
    if not columns:
        columns_str = '*'
    elif type(columns) == str:
        columns_str = columns
    else:
        columns_str = ', '.join(columns)
    return columns_str


def where_string(**kwargs):
    where_list = []
    for key, value in kwargs.items():
        if type(value) == str:
            if '.' not in value:
                value = f"'{value}'"
        string = f"""{key} = {value}"""
        where_list.append(string)
    where_str = ''
    if where_list:
        where_str = f"""WHERE {' AND '.join(where_list)}"""
    return where_str

