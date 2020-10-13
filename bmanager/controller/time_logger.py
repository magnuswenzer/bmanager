import datetime
import os
from pathlib import Path

from bmanager import exceptions
from bmanager.controller.base import BaseController
from bmanager.controller.project import ProjectController

import pickle

from bmanager import config
from bmanager import model


class TimeLogger:
    def __init__(self):
        self._start = None
        self._end = None
        self.is_finished = False
        self.is_logging = False

    def start(self):
        if self.is_logging or self.is_finished:
            return False
        self._start = datetime.datetime.now()
        self.is_logging = True
        return True

    def stop(self):
        if not self.is_logging:
            return False
        self._end = datetime.datetime.now()
        if self._end.date() != self._start.date():
            self._end = datetime.datetime(self._start.year, self._start.month, self._start.day, 23, 59, 59)
        self.is_logging = False
        self.is_finished = True
        return True

    def get_logged_time(self):
        if self.is_finished:
            return self._end - self._start
        elif self._start:
            return datetime.datetime.now() - self._start
        else:
            return datetime.timedelta()


class ProjectTimeLogger:

    def __init__(self, project_name):
        self.name = project_name
        self.time_loggers = []
        self.is_logging = False

    @property
    def latest_logger(self):
        if not self.time_loggers:
            return False
        return self.time_loggers[-1]

    def _latest_is_finished(self):
        if not self.latest_logger:
            return True
        if self.latest_logger.is_finished:
            return True
        return False

    def start(self):
        if not self._latest_is_finished():
            return False
        time_logger = TimeLogger()
        time_logger.start()
        self.time_loggers.append(time_logger)
        self.is_logging = True
        return True

    def stop(self):
        if self._latest_is_finished():
            return False
        time_logger = self.time_loggers[-1]
        time_logger.stop()
        self.is_logging = False
        return True

    @property
    def total_time(self):
        return sum_timedelta([tlog.get_logged_time() for tlog in self.time_loggers])


class ProjectsTimeLogger:

    def __init__(self):
        self.date = datetime.datetime.now().date()
        self.identifier = str(self.date)
        self.project_time_loggers = {}
        self.project_logging = None
        self.locked = False

    def stop_if_not_the_same_date(self):
        if datetime.datetime.now().date() > self.date:
            self._stop_active_project()

    def _check_project(self, project_name):
        if not self.project_time_loggers.get(project_name):
            raise exceptions.BmanagerException('Project not added to time_logger')

    def _stop_active_project(self):
        if not self.project_logging:
            return
        self.project_time_loggers.get(self.project_logging).stop()

    def _start_active_project(self):
        if not self.project_logging:
            return
        self.project_time_loggers.get(self.project_logging).start()

    @classmethod
    def from_pickle(cls, pickle_file_path):
        print(pickle_file_path)
        with open(pickle_file_path, 'rb') as fid:
            saved_object = pickle.load(fid)
        new_object = cls()
        new_object.date = saved_object.date
        new_object.identifier = saved_object.identifier
        new_object.project_time_loggers = saved_object.project_time_loggers
        new_object.project_logging = saved_object.project_logging
        new_object.locked = saved_object.locked
        return new_object

    def save(self, directory):
        file_path = Path(directory, f'{self.identifier}{get_logger_suffix()}')
        with open(file_path, 'wb') as fid:
            pickle.dump(self, fid)

    def add_project(self, project_name):
        """
        :param project_name: str
        :return:
        """
        if self.project_time_loggers.get(project_name):
            return
        self.project_time_loggers[project_name] = ProjectTimeLogger(project_name)

    def add_projects(self, project_list):
        for proj in project_list:
            self.add_project(proj)

    @property
    def project_list(self):
        return sorted(self.project_time_loggers)

    def start(self, project_name):
        self._check_project(project_name)
        if self.project_logging == project_name:
            return
        self._stop_active_project()
        self.project_logging = project_name
        self._start_active_project()

    def stop(self):
        self._stop_active_project()
        self.project_logging = None

    def get_report(self):
        report = {}
        for proj in self.project_list:
            logger = self.project_time_loggers.get(proj)
            logged_time = logger.total_time
            report[proj] = logged_time
        return report


class TimeLoggerController(BaseController):
    def __init__(self, model=None, project_list=[]):
        super().__init__()
        self.model = None
        self.project_controller = None

        self._project_list = project_list

        if model:
            self.model = model
            self.project_controller = ProjectController(model=self.model)
        self.save_directory = Path(Path(__file__).parent, 'time_report')

        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)

        self.loggers = {}
        self.active_logger = None

        self._load_saved_loggers()

    @property
    def project_list(self):
        if self.project_controller:
            return self.project_controller.get_project_name_list()
        else:
            return self._project_list

    def _load_saved_loggers(self):
        for file_name in os.listdir(self.save_directory):
            if not file_name.endswith(get_logger_suffix()):
                continue
            file_path = Path(self.save_directory, file_name)
            logger = ProjectsTimeLogger.from_pickle(file_path)
            logger.stop_if_not_the_same_date()
            logger.save(self.save_directory)
            self.loggers[logger.identifier] = logger

    def _save_logger(self, identifier):
        logger = self.loggers.get(identifier)
        logger.save(self.save_directory)

    def activate_logger(self):
        identifier = get_logger_identifier_string()
        self.active_logger = self.loggers.setdefault(identifier, ProjectsTimeLogger())
        self.active_logger.add_projects(self.project_list)

    def start_logger(self, project_name):
        if not self.active_logger:
            return False
        self.active_logger.start(project_name)
        self.active_logger.save(self.save_directory)
        return True

    def stop_logger(self):
        if not self.active_logger:
            return False
        self.active_logger.stop()
        self.active_logger.save(self.save_directory)
        return True

    def delete_logger(self, identifier):
        pass

    def get_current_project_logging(self):
        if not self.active_logger:
            return ''
        proj = self.active_logger.project_logging
        if not proj:
            return ''
        return proj

    def get_logger_report(self, identifier=None, as_string=False):
        if not identifier:
            identifier = get_logger_identifier_string()
        logger = self.loggers.get(identifier, None)
        if not logger:
            return None
        report = logger.get_report()
        tot = sum_timedelta([value for key, value in report.items()])
        if as_string:
            rep = {}
            for key, value in report.items():
                rep[key] = get_hour_minute_string_from_timedelta(value)
            t = get_hour_minute_string_from_timedelta(tot)
            return {identifier: {'all': rep,
                                 'tot': t}}
        return {identifier: {'all': report,
                             'tot': tot}}

    def get_logger_report_with_suggestions(self, identifier=None):
        rep = self.get_logger_report(identifier=identifier, as_string=True)
        if not rep:
            return {}
        tot = rep[identifier]['tot']
        h, m = tot.split(':')
        tot_hh = str(int(h) + round(int(m) / 60))
        rep_with_sug = {identifier: {'all': {},
                                     'tot': {'logged': tot,
                                             'suggestion': tot_hh}}}
        for key, value in rep[identifier]['all'].items():
            h, m = value.split(':')
            hh = str(int(h) + round(int(m)/60))
            rep_with_sug[identifier]['all'][key] = {'logged': value,
                                                    'suggestion': hh}

        return rep_with_sug


def get_date_string(date):
    if type(date) == datetime.datetime:
        date = str(date)
    return date[:10]


def get_dates_in_week(week, as_string=True):
    # week is in format YYYY-v
    d1 = datetime.datetime.strptime(week + '-1', "%G-%V-%u")
    dates = []
    for day in range(7):
        d = d1 + datetime.timedelta(days=day)
        if as_string:
            d = get_date_string(d)
        dates.append(d)
    return dates


def get_hour_minute_string_from_timedelta(timedelta_object):
    if not timedelta_object:
        # return ''
        return '0:00'
    tot_sec = timedelta_object.seconds
    hours = tot_sec // 3600
    minutes = tot_sec % 3600 // 60
    minutes = str(minutes).zfill(2)
    return f'{hours}:{minutes}'


def get_logger_suffix():
    return '.logger'


def get_logger_identifier_string():
    return str(datetime.datetime.now())[:10]


def sum_timedelta(timedelta_list):
    if not timedelta_list:
        return None
    dt_sum = timedelta_list[0]
    if len(timedelta_list) > 1:
        for dt in timedelta_list[1:]:
            if not dt:
                continue
            dt_sum += dt
    return dt_sum


if __name__ == '__main__':
    config = config.ModelConfig()
    model = model.Model(config=config)
    model.login()

    handler = TimeLoggerController(model=model)
    handler.activate_logger()

    report = handler.get_logger_report_with_suggestions('2020-08-25')
    print(handler.project_list)



    # t1 = datetime.datetime(2020, 8, 24, 17, 2, 23)
    # t2 = datetime.datetime.now()
    # dt = t2 - t1
    # print(get_hour_minute_string_from_timedelta(dt))
