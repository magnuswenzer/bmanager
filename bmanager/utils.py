import datetime
import json


class UtilsException(Exception):
    pass


def get_datetime_synonyms():
    """
    Returns a list of synonyms that should be seen (or converted) into datetime objects.
    :return:
    """
    return ['time', 'date', 'start_date', 'end_date']


def get_time_string_formats():
    time_formats = ['%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d']
    return time_formats


def get_datetime_from_string(time_string):
    time_formats = get_time_string_formats()
    for tf in time_formats:
        try:
            datetime_object = datetime.datetime.strptime(time_string, tf)
            return datetime_object
        except:
            pass
    raise UtilsException(f'Invalid time string format {time_string}')


def list_from_dict_list(dict_list, key, only_activated=False, include_hidden=False):
    """
    Returns a list of the value matching the key for each dict in the given dict_list.
    :param dict_list: list och dicts
    :param key: key in the dicts
    :param only_activated: boolean
    :return: list
    """
    return_list = []
    for d in dict_list:
        if only_activated and not d.get('activated'):
            continue
        if not include_hidden and d.get('hidden'):
            continue
        return_list.append(d.get(key))
    return return_list


def dict_from_dict_list(dict_list, key_key, value_key, only_activated=False, include_hidden=False):
    """
    :param dict_list: list och dicts
    :param key_key: key to be used as key in return dict
    :param value_key: key to be used as value in return dict
    :param only_activated: boolean
    :return: dict
    """
    return_dict = {}
    for key, value in zip(list_from_dict_list(dict_list, key_key, only_activated=only_activated, include_hidden=include_hidden),
                          list_from_dict_list(dict_list, value_key, only_activated=only_activated, include_hidden=include_hidden)):
        return_dict[key] = value
    return return_dict


def split_list_of_dicts_by_day(list_of_dicts, key, day_as_string=False):
    return_dict = {}
    for dic in list_of_dicts:
        print(dic)
        time = dic.get(key, None)
        if not time:
            continue
        time_day = time.date()
        if day_as_string:
            time_day = time_day.strftime('%Y-%m-%d')
        return_dict.setdefault(time_day, [])
        return_dict[time_day].append(dic)
    return return_dict


def get_lists_from_dicts_in_list(list_with_dicts, *keys):
    return_list = [[] for _ in range(len(keys))]
    for dic in list_with_dicts:
        for i, key in enumerate(keys):
            return_list[i].append(dic.get(key))
    return return_list


def load_json(file_path):
    with open(file_path) as fid:
        data = json.load(fid)
    return data


def save_json(data, file_path):
    with open(file_path, 'w') as fid:
        json.dump(data, fid)


