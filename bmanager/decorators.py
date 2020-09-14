from . import exceptions


def check_exceptions(func):
    """
    1: DatabaseUniqueConstraint
    2: MissingPrimaryKey
    9: Unknown error

    :param func:
    :return:
    """
    def new_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.AlreadyInDatabase:
            return 1
        except exceptions.MissingPrimaryKey:
            return 2
        except Exception:
            return 9
    return new_func