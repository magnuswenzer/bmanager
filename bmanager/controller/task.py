from bmanager import config
from bmanager import model
from bmanager.controller.base import TableBaseController
from bmanager.controller.employee import EmployeeController
from bmanager import exceptions


class TaskController(TableBaseController):
    def __init__(self, model=None):
        super().__init__(model=model)
        self.table_name = 'Task'
        self.employee_controller = EmployeeController(self.model)

    def add(self, **data):
        data['employee_id'] = self.employee_controller.get_id(user_name=self.model.user)
        self.model.add_record(self.table_name, **data)

    def get(self):
        return self.get_content_info()


if __name__ == '__main__':
    config = config.ModelConfig()
    model = model.Model(config=config)
    model.login()

    task = TaskController(model=model)

