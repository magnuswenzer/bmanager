from bmanager import config
from bmanager import model
from bmanager.controller.base import TableBaseController


class ProjectController(TableBaseController):
    def __init__(self, model=None):
        super().__init__(model=model)
        self.table_name = 'project'


if __name__ == '__main__':
    config = config.ModelConfig()
    model = model.Model(config=config)
    model.login()

    proj = ProjectController(model=model)
    col_info = proj.get_columns_info()
    cont = proj.get_content_info()
    data = cont['data']
    info = cont['info']

    