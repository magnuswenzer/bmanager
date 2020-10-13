import os
import sqlite3
from sqlite3 import Error
import importlib
from bmanager import exceptions


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    print('module', module)
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_database(database_info):
    """
    Creates and returns an object of a subclass to Database based on information in database_info.

    :param database_info: dict
    :return: Database subclass
    """
    print('db_class', f'{database_info.get("module")}.{database_info.get("class")}')
    db_class = get_class(f'{database_info.get("module")}.{database_info.get("class")}')

    return db_class(**database_info.get("initiation"))


class Database(object):

    def create_database(self):
        raise exceptions.MethodNotImplemented

    def create_tables(self, table_list):
        raise exceptions.MethodNotImplemented

    def add_to_table(self, table, **kwargs):
        raise exceptions.MethodNotImplemented

    def get_from_table(self, table, columns=[], **kwargs):
        raise exceptions.MethodNotImplemented

    def get_query(self, query):
        raise exceptions.MethodNotImplemented

    def update_table(self, table, data, **kwargs):
        raise exceptions.MethodNotImplemented



