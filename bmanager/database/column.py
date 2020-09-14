

class Column(dict):

    def __init__(self, column_info):
        """
        :param column_info: dict

            "name": "time",
            "display_name": "Datum",
            "data_type": "timestamp",
            "primary_key": true,
            "mandatory": true,
            "activated": true,
            "hidden": true

        """
        for key, value in column_info.items():
            self[key] = value
            setattr(self, key, value)

