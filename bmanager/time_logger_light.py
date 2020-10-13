import os
import datetime
import codecs
from pathlib import Path

from bmanager.controller.time_logger import TimeLoggerController
from bmanager.controller import time_logger
from bmanager.controller.time_logger import ProjectsTimeLogger


class Menu: 
    sep_length = 30

    def _print_top(self, header):
        os.system('clear')
        print()
        print()
        print('='*self.sep_length)
        print(header) 
        print('-'*self.sep_length)
        
    def _print_bottom(self):
        print('-'*self.sep_length) 
        
    def _print_menu(self, *args):
        pass 
        
    def _user_input(self):
        pass
        
    def show(self, *args):
        self._print_menu()
        self._user_input()


class MenuMain(Menu): 

    def __init__(self, parent):
        self.parent = parent 
        
    def _print_menu(self):
        self._print_top('Huvudmeny')
        print('L) Logga tid')
        print('R) Rapport')
        print('Q) Avsluta')
        self._print_bottom()
        
    def _user_input(self): 
        allowed = ['L', 'R', 'Q'] 
        answer = ''
        while answer not in allowed:
            answer = input('Välj: ') 
            answer = answer.upper()
            
        if answer == 'L': 
            self.parent.show_logger_menu()
        elif answer == 'R': 
            self.parent.show_report_menu()
        elif answer == 'Q': 
            self.parent.quit()


class MenuLogger(Menu): 

    def __init__(self, parent):
        self.parent = parent
        self.projects = self.parent.projects

    def _print_menu(self):
        self._print_top(f'Logga tid (Nu loggas: {self.parent.logger_object.get_current_project_logging()})')
        print('S) Stoppa')
        for nr, proj in self.projects.items():
            print(f'{nr}) {proj}')
        print()
        print('B) Bakåt')
        print('H) Huvudmeny')
        print('Q) Avsluta')
        self._print_bottom()
        
    def _user_input(self):
        allowed = ['S', 'B', 'H', 'Q'] + list(self.projects.keys())
        answer = ''
        while answer not in allowed:
            answer = input('Välj: ') 
            answer = answer.upper()
        if answer == 'S': 
            self.parent.stop_logger()
            self.show()
        elif answer == 'B':
            self.parent.show_main_menu()
        elif answer == 'H':
            self.parent.show_main_menu()
        elif answer == 'Q': 
            self.parent.quit()
        else:
            self.parent.start_logger(self.projects[answer])
            self.show()
            

class MenuReport(Menu): 

    def __init__(self, parent):
        self.parent = parent
        
    def _print_menu(self):
        self._print_top('Välj typ av rapport')
        print('<Return> för dagens datum')
        print('Format 24/5 för dag')
        print('Format v12 för vecka')
        print('B) Bakåt')
        print('H) Huvudmeny')
        print('Q) Avsluta')
        self._print_bottom()
        
    def _user_input(self): 
        week = None
        day = None 
        month = None
        menu = None
        while not any([week, day, menu]):
            try:
                answer = input('Välj: ').strip()
                print('#', answer)
                if answer == '':
                    d = datetime.datetime.now()
                    day = d.day 
                    month = d.month
                elif answer.upper() in ['B', 'H', 'Q']:
                    menu = answer.upper()
                elif answer.startswith('v'): 
                    week = int(answer[1:].strip())
                elif '/' in answer:
                    day, month = [int(item.strip().strip("'").strip('"')) for item in answer.split('/')]
                    print(day, month)
            except Exception as e:
                print(e)
                raise
        if week:
            year = datetime.datetime.now().year
            week_str = f'{year}-{week}'
            self.parent.show_week_report(week_str)
        elif month and day:
            year = datetime.datetime.now().year
            date = datetime.datetime(year, month, day)
            date_str = date.strftime('%Y-%m-%d')
            self.parent.show_day_report(date_str)
        elif menu:
            if menu == 'B':
                self.parent.show_main_menu()
            elif menu == 'H':
                self.parent.show_main_menu()
            elif menu == 'Q':
                self.parent.quit()
            
            
class MenuDayReport(Menu): 

    def __init__(self, parent):
        self.parent = parent
        
    def _print_menu(self, logged_data):
        day_str = list(logged_data.keys())[0]
        self._print_top(f'Tidrapport: {day_str}')
        for proj in logged_data[day_str]['all'].keys():
            print(f'{proj: <10}{logged_data[day_str]["all"][proj]["logged"]: <10}{logged_data[day_str]["all"][proj]["suggestion"]: <10}')

        self._print_bottom()
        print(f'Tot: {logged_data[day_str]["tot"]["logged"]} ({logged_data[day_str]["tot"]["suggestion"]})')
        self._print_bottom()
        print('B) Bakåt')
        print('H) Huvudmeny')
        print('Q) Avsluta')
        self._print_bottom()

    def _user_input(self):
        allowed = ['B', 'Q', 'H']
        answer = ''
        while answer not in allowed:
            answer = input('Välj: ')
            answer = answer.upper()
        if answer == 'B':
            self.parent.show_report_menu()
        elif answer == 'H':
            self.parent.show_main_menu()
        elif answer == 'Q':
            self.parent.quit()
        
    def show(self, logged_data):
        self._print_menu(logged_data)
        self._user_input()


class MenuWeekReport(Menu):

    def __init__(self, parent):
        self.parent = parent

    def _print_menu(self, week_str, logged_data):
        self._print_top(f'Tidrapport: {week_str}')
        header = f'{"": <15}'
        proj_set = set()
        for day_str in logged_data:
            header = f'{header}{day_str: <15}'
            if not logged_data[day_str]:
                continue
            for proj in logged_data[day_str]['all'].keys():
                proj_set.add(proj)
        proj_list = sorted(proj_set)
        print(header)

        for proj in proj_list:
            line_string = f'{proj: <15}'
            for day_str in logged_data:
                if not logged_data[day_str]:
                    line_string = f'{line_string}{"": <15}'
                    continue
                if proj in logged_data[day_str]['all']:
                    item = f'{logged_data[day_str]["all"][proj]["logged"]} ({logged_data[day_str]["all"][proj]["suggestion"]})'
                line_string = f'{line_string}{item: <15}'
            line_string = line_string.replace('0:00 (0)', ' '*8)
            print(line_string)

        print()
        line_string = f'{"Totalt": <15}'
        for day_str in logged_data:
            if not logged_data[day_str]:
                line_string = f'{line_string}{"": <15}'
                continue
            item = f'{logged_data[day_str]["tot"]["logged"]} ({logged_data[day_str]["tot"]["suggestion"]})'
            line_string = f'{line_string}{item: <15}'
        line_string = line_string.replace('0:00 (0)', ' ' * 8)
        print(line_string)


        self._print_bottom()
        # print(f'Tot: {logged_data[day_str]["tot"]["logged"]} ({logged_data[day_str]["tot"]["suggestion"]})')
        self._print_bottom()
        print('B) Bakåt')
        print('H) Huvudmeny')
        print('Q) Avsluta')
        self._print_bottom()

    def _user_input(self):
        allowed = ['B', 'Q', 'H']
        answer = ''
        while answer not in allowed:
            answer = input('Välj: ')
            answer = answer.upper()
        if answer == 'B':
            self.parent.show_report_menu()
        elif answer == 'H':
            self.parent.show_main_menu()
        elif answer == 'Q':
            self.parent.quit()

    def show(self, week_str, logged_data):
        self._print_menu(week_str, logged_data)
        self._user_input()


class TimeLoggerLight:
    def __init__(self):
        self.projects_file_path = Path(Path(__file__).parent, 'projects.txt')
        self._load_projects()

        self.logger_object = TimeLoggerController(project_list=self.project_list)
        self.logger_object.activate_logger()

        self.menu_main = MenuMain(self)
        self.menu_logger = MenuLogger(self)
        self.menu_report = MenuReport(self)
        self.menu_day_report = MenuDayReport(self)
        self.menu_week_report = MenuWeekReport(self)

    def _load_projects(self):
        if not self.projects_file_path.exists():
            with codecs.open(self.projects_file_path, 'w', encoding='cp1252') as fid:
                pass
        self.projects = {}
        with codecs.open(self.projects_file_path, encoding='cp1252') as fid:
            nr = 0
            for line in fid:
                proj = line.strip()
                if not proj:
                    continue
                nr += 1
                self.projects[str(nr)] = proj
        self.project_list = list(self.projects.values())

    def start_logger(self, proj):
        self.logger_object.start_logger(proj)
    
    def stop_logger(self): 
        self.logger_object.stop_logger()
        
    def show_main_menu(self): 
        self.menu_main.show()
        
    def show_logger_menu(self): 
        self.menu_logger.show()
        
    def show_report_menu(self): 
        self.menu_report.show() 
        
    def show_day_report(self, date_str): 
        data = self.logger_object.get_logger_report_with_suggestions(date_str)
        self.menu_day_report.show(data)
        
    def show_week_report(self, week_str):
        dates = time_logger.get_dates_in_week(week=week_str, as_string=True)
        data = {}
        for date_str in dates:
            d = self.logger_object.get_logger_report_with_suggestions(date_str)
            if d:
                data.update(d)
            else:
                data[date_str] = {}
        self.menu_week_report.show(week_str, data)
        
    def run(self):
        self.show_main_menu()
        
    def quit(self):
        pass


if __name__ == '__main__':
    app = TimeLoggerLight()
    app.run()

