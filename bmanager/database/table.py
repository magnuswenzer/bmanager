from bmanager.database.column import Column
from bmanager import exceptions


def get_table_info_object(table_name, config_object=None):
    return TableInfo(table_name, config_object=config_object)


def get_table_content_object(table_name, config_object=None, database_object=None, table_info_object=None):
    if not table_info_object:
        table_info_object = get_table_info_object(table_name, config_object=config_object)
    return TableContent(table_info_object=table_info_object, database_object=database_object)


def get_table_record_object(table_name, config_object=None, database_object=None, table_info_object=None, table_content_object=None, **kwargs):
    if not table_content_object:
        table_content_object = get_table_content_object(table_name,
                                                        config_object=config_object,
                                                        database_object=database_object,
                                                        table_info_object=table_info_object)
    return TableRecord(table_content_object=table_content_object, **kwargs)


class TableInfo(object):

    def __init__(self, table_name, config_object=None):
        self.config = config_object
        self.table_name = table_name

        self.table_info = {}
        self.column_objects = {}
        self.all_columns = []
        self.mandatory_columns = []
        self.visible_columns = []
        self.primary_key = None

        self._load_info()

    def _load_info(self):
        for table in self.config.get_tables_info():
            print(self.table_name, 'table', table)
            if table.get('name') == self.table_name:
                self.table_info = table
        for column in self.table_info.get('columns'):
            column_name = column.get('name')
            column_object = Column(column)
            if not column_object.get('activated'):
                continue
            # if column_object.get('hidden'):
            #     continue
            if column_object.get('primary_key'):
                self.primary_key = column_name
            self.all_columns.append(column_name)
            self.column_objects[column_name] = column_object
            self.visible_columns.append(column_name)
            if column_object.get('mandatory'):
                if not column_object.get('not_in_db', False):
                    self.mandatory_columns.append(column_name)

    def has_column(self, column_name):
        if self.column_objects.get(column_name):
            return True
        return False

    def get_column_info(self, *args, as_list=False):
        if not args:
            print('not args', type(self.column_objects))
            if as_list:
                print('as list')
                return [self.column_objects[key] for key in self.all_columns]
            print('return')
            return self.column_objects
        rl = [[] for _ in range(len(args))]
        for col in self.all_columns:
            col_obj = self.column_objects.get(col)
            for i, arg in enumerate(args):
                rl[i].append(col_obj.get(arg))
        return rl

    # rl = []
    # for col in self.all_columns:
    #     col_obj = self.column_objects.get(col)
    #     cl = []
    #     for i, arg in enumerate(args):
    #         cl.append(col_obj.get(arg))
    #     rl.append(tuple(cl))
    # return rl

    def get_display_name(self, column_name):
        if type(column_name) == str:
            return self.column_objects[column_name]['display_name']
        elif type(column_name) == list:
            rl = []
            for col_name in column_name:
                rl.append(self.column_objects[col_name]['display_name'])
            return rl


class TableContent(object):
    """
    Handles multiple data from a table.
    """
    def __init__(self, table_info_object=None, database_object=None):
        self.info = table_info_object
        self.db = database_object

        self.table_name = self.info.table_name
        self.primary_key = self.info.primary_key

    def get_primary_key_list(self):
        key_list = self.db.get_from_table(self.table_name, columns=[self.primary_key])
        return [item.get(self.primary_key) for item in key_list]

    def get_content_list(self, *args, **kwargs):
        """
        Returns a list of dicts. dicts contains args as keys. Option to set sort. Default soting is primary key.
        """
        if not args:
            args = self.info.all_columns
        return self.db.get_from_table(self.table_name, columns=args, **kwargs)

    def get_content_dict(self, *args):
        print('args', args)
        content_list = self.get_content_list(*args)
        print('content_list', content_list)
        content = {}
        for cont in content_list:
            content[cont.get(self.info.primary_key)] = cont
        return content


class TableRecord(object):
    """
    Handles information on from a single row in a database table.
    """

    def __init__(self, table_content_object=None, **kwargs):
        self.content = table_content_object

        self.info = self.content.info
        self.db = self.content.db
        self.table_name = self.info.table_name
        self.primary_key = self.info.primary_key

        self.data = {}
        self._id = None

        self._load_from_db(**kwargs)

    def _has_data(self):
        if self.data:
            return True
        return False

    def _has_primary_key(self):
        if self.data.get(self.primary_key):
            return True
        return False

    def _in_db(self):
        if not self._has_data:
            return None
        kw = {self.primary_key: self._id}
        if self.db.get_from_table(self.table_name, columns=[], **kw):
            return True
        return False

    def add_data(self, **kwargs):
        for key, value in kwargs.items():
            if not self.info.has_column(key):
                continue
            self.data[key] = value
            if key == self.info.primary_key:
                self._id = value

    def has_data(self):
        return self._has_data()

    def _load_from_db(self, **kwargs):
        if not kwargs:
            return
        self.data = {}
        result = self.db.get_from_table(self.table_name, columns=[], **kwargs)
        self.data = result[0]
        self._id = self.data.get('id')

    def missing_mandatory_columns(self):
        missing = []
        for col in self.info.mandatory_columns:
            if not self.data.get(col):
                missing.append(col)
        return missing

    @property
    def primary_key_data(self):
        return self.data.get(self.primary_key)

    def save(self):
        """
        Returns True if successful else False.
        :return:
        """
        missing = self.missing_mandatory_columns()
        if missing:
            raise exceptions.MissingMandatory(missing)

        if self._id:
            self.db.update_table(self.table_name, self.data, id=self._id)
        else:
            self.db.add_to_table(self.table_name, **self.data)
        return True

    def set_data(self, **kwargs):
        self.data = {}
        self.add_data(**kwargs)

