from bmanager import exceptions


class TableBaseController:
    def __init__(self, model=None):
        self.table_name = ''
        self.model = model
        self.user = self.model.user

    def add(self, **data):
        self.model.add_record(self.table_name, **data)

    def update(self, data, **kwargs):
        self.model.update_record(self.table_name, data, **kwargs)

    def get_columns_info(self, as_list=False):
        return self.model.get_columns_info(self.table_name, as_list=as_list)

    def get_columns_names(self):
        return [item.get('name') for item in self.get_columns_info(as_list=True)]

    def get_content_info(self, **kwargs):
        return self.model.get_content_list(self.table_name, **kwargs)

    def get_id(self, **kwargs):
        result = self.model.get_content_list(self.table_name, **kwargs)
        return result[0].get('id')
