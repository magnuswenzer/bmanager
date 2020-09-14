from bmanager.config import ModelConfig
from bmanager.database.db import get_database
from bmanager.database import table


class Model(object):
    def __init__(self, config):
        self.config = config
        self.db = None

        self.user = None  # user_name in employee

        self.login()

    def _check_authorization(self, username=None, password=None):
        """
        Check authentication here.
        :param username:
        :param password:
        :return:
        """
        self.user = 'admin'
        return True

    def _get_table_content_object(self, table_name):
        return table.get_table_content_object(table_name,
                                              config_object=self.config,
                                              database_object=self.db)

    def _get_table_info_object(self, table_name):
        """
        :param table_name:
        :return:
        """
        return table.get_table_info_object(table_name,
                                           config_object=self.config)

    def _get_table_record_object(self, table_name, **kwargs):
        return table.get_table_record_object(table_name,
                                             config_object=self.config,
                                             database_object=self.db,
                                             **kwargs)
    
    def _initiate_database(self):
        self.db = get_database(self.config.database)
        self.db.create_tables(self.config.tables)

    def add_record(self, table_name, **data):
        table_record = self._get_table_record_object(table_name)
        table_record.set_data(**data)
        table_record.save()

    def update_record(self, table_name, data, **kwargs):
        table_record = self._get_table_record_object(table_name, **kwargs)
        table_record.add_data(**data)
        table_record.save()

    def get_columns_info(self, table_name, as_list=False):
        info_object = self._get_table_info_object(table_name)
        return info_object.get_columns_info(as_list=as_list)

    def get_content_list(self, table_name, *args, **kwargs):
        content_object = self._get_table_content_object(table_name)
        return content_object.get_content_list(*args, **kwargs)

    def login(self, username=None, password=None):
        if self._check_authorization(username=username, password=password):
            self._initiate_database()


if __name__ == '__main__':
    config = ModelConfig()
    c = Model(config=config)
    c.login()














