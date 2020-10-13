import datetime

from bmanager import exceptions
from bmanager.config import ModelConfig
from bmanager.controller.employee import EmployeeController
from bmanager.controller.project import ProjectController
from bmanager.controller.task import TaskController
from bmanager.controller.work_plan import WorkPlanController
from bmanager.controller.work_report import WorkReportController
from bmanager.controller.time_logger import TimeLoggerController
from bmanager.model import Model

if __name__ == '__main__':
    config = ModelConfig(activate='test_local')
    model = Model(config=config)
    model.login()

    # Projects
    pc = ProjectController(model=model)
    projects = [dict(project_name='proj1'),
                dict(project_name='proj2',
                     comment='detta ar ett test'),
                dict(project_name='proj3')]
    for proj in projects:
        try:
            pc.add(**proj)
        except exceptions.AlreadyInDatabase:
            pc.update(proj, project_name=proj.get('project_name'))

    # Employee
    ec = EmployeeController(model=model)
    employees = [dict(user_name='magw',
                      first_name='Magnus',
                      last_name='Wenzer',
                      role='admin'),
                 dict(user_name='kfin',
                      first_name='Karin',
                      last_name='Fingal',
                      role='employee')]

    for e in employees:
        try:
            ec.add(**e)
        except exceptions.AlreadyInDatabase:
            ec.update(e, user_name=e.get('user_name'))

    # Work plan
    wpc = WorkPlanController(model=model)
    wpc.add('proj1', 'magw', 40)

    # Time report
    tlc = TimeLoggerController(model=model)
    tlc.activate_logger()
    print(tlc.project_list)

    # Work report
    wrc = WorkReportController(model=model)
    wrc.add(project_name='proj1', date=datetime.datetime.now(), hours_reported=5)
    wrc.add(project_name='proj2', date=datetime.datetime.now(), hours_reported=1)
    wrc.add(project_name='proj3', date=datetime.datetime.now(), hours_reported=2)

    # Tasks
    tc = TaskController(model=model)
    task_columns = tc.get_column_names()

    tc.add(task='uppdatera mera')

