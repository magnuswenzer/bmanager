from bmanager import exceptions
from bmanager.config import ModelConfig
from bmanager.controller.employee import EmployeeController
from bmanager.controller.project import ProjectController
from bmanager.controller.task import TaskController
from bmanager.model import Model

if __name__ == '__main__':
    config = ModelConfig(activate='test_local')
    model = Model(config=config)
    model.login()

    # Projects
    project_controller = ProjectController(model=model)
    projects = [dict(project_name='test project 1'),
                dict(project_name='test project 2',
                     comment='detta ar ett test'),
                dict(project_name='test project 3')]
    for proj in projects:
        try:
            project_controller.add(**proj)
        except exceptions.AlreadyInDatabase:
            project_controller.update(proj, project_name=proj.get('project_name'))

    # Employee
    emp_controller = EmployeeController(model=model)
    employees = [dict(user_name='magw',
                      first_name='Magnus',
                      last_name='Wenzer'),
                 dict(user_name='kfin',
                      first_name='Karin',
                      last_name='Fingal')]

    for e in employees:
        try:
            emp_controller.add(**e)
        except exceptions.AlreadyInDatabase:
            emp_controller.update(e, user_name=proj.get('user_name'))

    # Tasks
    task_controller = TaskController(model=model)
    task_columns = task_controller.get_columns_names()

