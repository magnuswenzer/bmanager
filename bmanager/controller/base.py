from bmanager import exceptions


class BaseController:

    def update(self):
        pass


class TableBaseController(BaseController):
    def __init__(self, model=None):
        super().__init__()
        self.table_name = ''
        self.model = model
        self.user = self.model.user

    def add(self, **data):
        self.model.add_record(self.table_name, **data)

    def update(self, data, **kwargs):
        self.model.update_record(self.table_name, data, **kwargs)

    def get_column_info(self, as_list=False):
        return self.model.get_column_info(self.table_name, as_list=as_list)

    def get_column_names(self, only_in_db=False):
        data = self.get_column_info(as_list=True)
        if only_in_db:
            data = [item for item in data if not item.get('not_in_db')]
        return_list = [item.get('name') for item in data]
        return return_list

    def get_content_info(self, **kwargs):
        return self.model.get_content_list(self.table_name, **kwargs)

    def get_id(self, **kwargs):
        result = self.model.get_content_list(self.table_name, **kwargs)
        return result[0].get('id')

