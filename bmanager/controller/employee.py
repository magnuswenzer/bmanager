from bmanager import config
from bmanager import model
from bmanager.controller.base import TableBaseController


class EmployeeController(TableBaseController):
    def __init__(self, model=None):
        super().__init__(model=model)
        self.table_name = 'employee'


if __name__ == '__main__':
    config = config.ModelConfig()
    model = model.Model(config=config)
    model.login()
