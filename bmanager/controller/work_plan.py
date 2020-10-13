from bmanager.controller.base import TableBaseController
from bmanager.controller.project import ProjectController
from bmanager.controller.employee import EmployeeController

from bmanager import exceptions


class WorkPlanController(TableBaseController):
    def __init__(self, model=None):
        super().__init__(model=model)
        self.table_name = 'WorkPlan'
        self.project_controller = ProjectController(model=self.model)
        self.employee_controller = EmployeeController(model=self.model)

    @property
    def project_list(self):
        return self.project_controller.get_project_name_list()

    @property
    def employee_list(self):
        return self.employee_controller.get_user_name_list()

    def add(self, project_name=None, user_name=None, hours_planed=None, **kwargs):
        proj_id = self.project_controller.get_id(project_name=project_name)
        emp_id = self.employee_controller.get_id(user_name=user_name)
        data = dict(project_id=proj_id,
                    employee_id=emp_id,
                    hours_planed=hours_planed)
        data.update(kwargs)
        try:
            self.model.add_record(self.table_name, **data)
        except exceptions.AlreadyInDatabase:
            data = dict(hours_planed=hours_planed)
            self.model.update_record(self.table_name, data, project_id=proj_id, employee_id=emp_id)



