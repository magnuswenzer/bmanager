import datetime

from bmanager.controller.base import TableBaseController
from bmanager.controller.employee import EmployeeController
from bmanager.controller.project import ProjectController

from bmanager import exceptions


class WorkReportController(TableBaseController):
    def __init__(self, model=None):
        super().__init__(model=model)
        self.table_name = 'WorkReport'
        self.project_controller = ProjectController(model=self.model)
        self.employee_controller = EmployeeController(model=model)
        self.all_controller_columns = self._get_columns_from_all_controllers()

    def _get_model_employee_id(self):
        return self.employee_controller.get_id(user_name=self.model.user)

    def _get_columns_from_all_controllers(self):
        all_columns = []
        all_columns.extend([f'{self.table_name}.{col}' for col in self.get_column_names(only_in_db=True)])
        all_columns.extend([f'{self.project_controller.table_name}.{col}' for col in self.project_controller.get_column_names(only_in_db=True)])
        all_columns.extend([f'{self.employee_controller.table_name}.{col}' for col in self.employee_controller.get_column_names(only_in_db=True)])
        return all_columns

    @staticmethod
    def _get_date(date):
        if type(date) == datetime.datetime:
            date = str(date)
        return date[:10]

    def _get_dates_in_week(self, week, as_string=True):
        # week is in format YYYY-v
        d1 = datetime.datetime.strptime(week + '-1', "%G-%V-%u")
        dates = []
        for day in range(7):
            d = d1 + datetime.timedelta(days=day)
            if as_string:
                d = self._get_date(d)
            dates.append(d)
        return dates

    def add(self, project_name=None, date=None, **kwargs):
        proj_id = self.project_controller.get_id(project_name=project_name)
        emp_id = self._get_model_employee_id()
        date = self._get_date(date)
        data = dict(employee_id=emp_id,
                    project_id=proj_id,
                    date=date)
        data.update(kwargs)

        try:
            self.model.add_record(self.table_name, **data)
        except exceptions.AlreadyInDatabase:
            d = data.pop('date')
            self.model.update_record(self.table_name,
                                     data,
                                     **dict(employee_id=emp_id, project_id=proj_id, date=d))

    def get_report(self, date=None, week=None):
        # Return full info with all fields divided into table names.
        if date:
            dates = [self._get_date(date)]
        elif week:
            dates = self._get_dates_in_week(week)
            
        report = {}
        for date in dates:
            report[date] = {}
            result = self._get_report_data(date)
            for item in result:
                report[date][item.get('Project.project_name')] = item
        return report

    def _get_report_data(self, date):
        columns = [col for col in self.all_controller_columns if not col.endswith('id')]
        query = f"""
                SELECT {', '.join(columns)}
                FROM WorkReport, Employee, Project
                WHERE Employee.user_name = '{self.user}' 
                AND WorkReport.date = '{date}'
                """
        result = self.model.get_query(query)
        data = {}
        for item in result:
            for col, val in zip(columns, item):
                t, c = col.split('.')
                data.setdefault(t, {})
                data[t][c] = val
        return data



