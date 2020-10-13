class BmanagerException(Exception):
    code = 9
    info = 'Unknown'


class AlreadyInDatabase(BmanagerException):
    code = 1
    info = 'Primary key already in database'


class MissingPrimaryKey(BmanagerException):
    code = 2
    info = 'Missing primary key'


class MissingMandatory(BmanagerException):
    code = 3
    info = 'Missing mandatory field'


class MissingData(BmanagerException):
    code = 4
    info = 'Missing data'


class MissingEmployee(BmanagerException):
    code = 5
    info = 'Missing employee'


class MissingProject(BmanagerException):
    code = 6
    info = 'Missing project'


class MethodNotImplemented(BmanagerException):
    code = 99
    info = 'Method not implemented'


class NoAdminRights(BmanagerException):
    code = 88
    info = 'Method not implemented'



