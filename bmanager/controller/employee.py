from bmanager import config
from bmanager import model
from bmanager.controller.base import TableBaseController
from bmanager import exceptions


class EmployeeController(TableBaseController):
    def __init__(self, model=None):
        super().__init__(model=model)
        self.table_name = 'Employee'

    def _confirm_admin(self):
        if not self.model.role == 'admin':
            raise exceptions.NoAdminRights
        return True

    def add(self, **data):
        self._confirm_admin()
        self.model.add_record(self.table_name, **data)

    def update(self, data, **kwargs):
        self._confirm_admin()
        self.model.update_record(self.table_name, data, **kwargs)

    def get_user_name_list(self):
        content = self.get_content_info()
        return [cont.get('user_name') for cont in content]

    def get_role(self, user_name):
        emp = self.get_content_info(user_name=user_name)
        if not emp:
            raise exceptions.MissingEmployee(user_name)
        return emp[0].get('role')


if __name__ == '__main__':
    config = config.ModelConfig()
    model = model.Model(config=config)
    model.login()
