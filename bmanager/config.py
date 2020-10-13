from pathlib import Path
import os
from . import utils


class ModelConfig(object):
    def __init__(self, config_file_path=None, activate=None):
        """
        :param config_file_path: json file with the configurations to set up the model.
        """
        if config_file_path:
            self.config_file_path = Path(config_file_path)
        else:
            # Default database setup
            self.config_file_path = Path(os.path.dirname(__file__), 'default_model_config.json')

        self.config = {}
        self.database = {}  # this is the database information
        self.tables = []

        self._load_config_file()
        self._activate(activate)
        self._set_database()

    def _activate(self, name):
        if not name:
            return
        for db in self.config.get('databases'):
            db['activated'] = False
            if db.get('name') == name:
                db['activated'] = True

    def _load_config_file(self):
        """
        Load the given config file
        :return:
        """
        self.config = utils.load_json(str(self.config_file_path))

    def _set_database(self):
        """
        Sets the database that is activated in the config file.
        Also sets the active tables.
        :return:
        """
        for db in self.config.get('databases'):
            if db.get('activated'):
                self.database = db
                break

        # Set active tables
        self.tables = []
        for table in self.config.get('tables'):
            if table.get('activated'):
                columns = []
                for col in table.get('columns'):
                    if col.get('activated'):
                        columns.append(col)
                table['columns'] = columns
                self.tables.append(table)

    def _get_table_columns(self, table, **kwargs):
        """
        kwargs options:
            only_activated: default is True
            only_mandatory: default is False
        """
        # table = table.capitalize()
        columns = []
        for tb in self.tables:
            if tb.get('name') == table:
                columns = tb.get('columns')[:]
                if kwargs.get('only_activated', True):
                    columns = [dic for dic in columns if dic.get('activated')]
                if kwargs.get('only_mandatory', False):
                    columns = [dic for dic in columns if dic.get('mandatory')]
                return columns

    def get_tables_info(self):
        return self.config.get('tables')

    def get_table_columns_mapping(self, table, from_col, to_col, **kwargs):
        table_columns = self._get_table_columns(table, **kwargs)
        column_mapping = {}
        for col in table_columns:
            column_mapping[col.get(from_col)] = col.get(to_col)
        return column_mapping

    def get_table_columns(self, table, **kwargs):
        return self._get_table_columns(table, **kwargs)

    def get_table_columns_by_key(self, table, key, **kwargs):
        table_columns = self._get_table_columns(table, **kwargs)
        by_key = {}
        for col in table_columns:
            by_key[col.get(key)] = col
        return by_key

    def get_table_column_names(self, table, **kwargs):
        table_columns = self._get_table_columns(table, **kwargs)
        return [col.get('name') for col in table_columns]




